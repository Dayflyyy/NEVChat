import json
import uuid
import pika
import redis
import asyncio

# Redis 客户端用于临时存储和查找结果
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

def convert_to_json(input_string):
    # 去除字符串两端的额外双引号
    cleaned_string = input_string.strip('"')

    # 对转义字符进行处理
    cleaned_string = cleaned_string.replace('\\"', '"')

    # 将处理后的字符串转换为JSON格式
    json_data = json.loads(cleaned_string)

    return json_data
# 消息队列模块
class MessageQueue:

    def __init__(self, queue_name='default_queue'):
        self.queue_name = queue_name
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=queue_name)

    def generate_request_id(self):
        return str(uuid.uuid4())

    def send_message(self, api_type, parameters):
        request_id = self.generate_request_id()
        message = {
            "api_type": api_type,
            "request_id": request_id,
            "parameters": parameters
        }
        self.channel.basic_publish(exchange='',
                                   routing_key=self.queue_name,
                                   body=str(message))
        return request_id

    async def wait_for_response(self, request_id, timeout=10):
        elapsed_time = 0
        while elapsed_time < timeout:
            # 检查 Redis 中是否存在以 request_id 为键的值
            if redis_client.exists(request_id):
                # 从 Redis 获取值并打印
                response = redis_client.get(request_id)
                print(f" [x] Redis response found for {request_id}: {response.decode('utf-8')}")

                # 获取后删除缓存
                redis_client.delete(request_id)
                # return convert_to_json(response.decode('utf-8'))
                return response.decode('utf-8')

            # 轮询间隔
            await asyncio.sleep(0.5)
            elapsed_time += 0.5

        raise TimeoutError("Waiting for response timed out.")

    def consume_messages(self):
        # 定义一个回调函数，用于处理从队列中收到的消息
        def callback(ch, method, properties, body):
            print(f" [x] Received {body}")

            message = json.loads(body)
            request_id = message.get("request_id")

            # 如果 request_id 和 data 都存在，写入 Redis
            if request_id:
                redis_client.set(request_id, "测试消息队列")
                print(f" [x] Stored message with request_id: {request_id}")
            else:
                print(f" [x] Invalid message format: {message}")

        # 订阅队列并设置回调函数
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=callback, auto_ack=True)

        print(' [*] Waiting for messages. To exit press CTRL+C')
        self.channel.start_consuming()

    def close_connection(self):
        self.connection.close()


# 测试代码
if __name__ == "__main__":
    # 创建队列对象
    queue = MessageQueue('test_queue')

    # 发送消息并获取 request_id
    request_id = queue.send_message(api_type="test_api", parameters={"key": "value"})
    print(f" [x] Sent message with request_id: {request_id}")


    # 消费者部分：开启一个新的线程/任务来消费消息
    def start_consumer():
        try:
            print(" [*] Starting message consumer...")
            queue.consume_messages()  # 消费消息队列中的消息
        except KeyboardInterrupt:
            print("Consumer stopped.")
        finally:
            queue.close_connection()


    # Redis 轮询部分：在发送消息后，轮询 Redis，检查是否有对应的结果
    async def poll_redis_for_response():
        try:
            print(f" [*] Polling Redis for response to request_id: {request_id}")
            response = await queue.wait_for_response(request_id)
            print(f" [x] Response received from Redis: {response}")
        except TimeoutError as e:
            print(f" [x] Redis polling timed out: {e}")
        finally:
            queue.close_connection()


    # 创建新的事件循环
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # 同时运行消费者和 Redis 轮询
    loop.run_until_complete(asyncio.gather(
        asyncio.to_thread(start_consumer),  # 消费者运行在单独的线程中
        poll_redis_for_response()  # 轮询 Redis
    ))

    # 关闭事件循环
    loop.close()
