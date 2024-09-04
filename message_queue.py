import uuid
import pika
import redis
import asyncio

# Redis 客户端用于临时存储和查找结果
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

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
            if redis_client.exists(request_id):
                response = redis_client.get(request_id)
                redis_client.delete(request_id)  # 获取后删除缓存
                return response.decode('utf-8')
            await asyncio.sleep(0.5)  # 轮询间隔，避免过于频繁查询
            elapsed_time += 0.5
        raise TimeoutError("Waiting for response timed out.")

    def close_connection(self):
        self.connection.close()
