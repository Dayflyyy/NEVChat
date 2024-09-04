from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from zhipuai import ZhipuAI
import json
import asyncio
import message_queue

app = FastAPI()
your_api_key = "3739459af48de127aee901616a603dff.N2KAwjsKTZKKtbfI"

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，实际生产中应根据需要调整
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有头信息
)

class ChatRequest(BaseModel):
    question: str
# async def call_zhipu_ai(message):
#     client = ZhipuAI(api_key=your_api_key)
#     response = await asyncio.to_thread(client.chat.completions.create(
#         model="glm-4-0520",
#         messages=message,
#     ))
#     return response.choices[0].message.content
#
#
# @app.post("/test")
# async def test(request:ChatRequest):
#
#     messages = [
#         {"role": "user",
#          "content": f"你是谁,{request.question}"},
#     ]
#     response = await call_zhipu_ai(message=messages)
#     return {"response": response}

@app.options("/chat")
async def options_handler():
    return {"status": "ok"}

@app.post("/chat")
async def chatresponse(request: ChatRequest):
    question = request.question
    client = ZhipuAI(api_key=your_api_key)  # 使用环境变量或者配置文件代替明文APIKey
    print(question)
    response = await asyncio.to_thread(client.chat.completions.create,
                                       model="glm-4-0520",  # 填写需要调用的模型编码
                                       messages=[
                                           {"role": "user",
                                            "content": "假设你作为一个新能源大数据平台的数据分析专家，请回答我的问题"},
                                           {"role": "assistant",
                                            "content": "当然，为了更精准的回答，请告诉我一些关于平台的信息和回答的具体格式要求"},
                                           {"role": "user",
                                            "content": "平台有全球新能源汽车销量总览，品牌销售情况概况，车型销售情况概况，汽车保有量状况，汽车充电桩分布，新能源汽车行业资讯六个大模块，我需要你根据用户的问题，给出基础的回答并提示用户可以选择去哪个版块寻找相应信息，其他的问题可以自由回答，控制字数在一定范围内即可"},
                                           {"role": "assistant", "content": "好的我了解了，请告诉我具体的格式"},
                                           {"role": "user",
                                            "content": "第一段文字优先用自然语言回答用户问题，第二段指引用户前往具体模块，请以markdown格式返回给我，字数不要太多，要求加粗关键文字并在适当处添加换行符，格式请严格依据首先以自然语言回复，然后在“您可以前往下面以下模块获得进一步的行业信息”下方逐个列出模块名的规范，下面是一个示例回答，：当前的新能源汽车市场正处于**快速发展期**，受到全球气候变化和能源转型的推动，以及各国政府政策的支持。/n**您可以前往下面以下模块获得进一步的行业信息**：/n**1.全球销量总览**/n**2.新能源行业资讯**"},
                                           {"role": "assistant", "content": "好的，请告诉我您的问题"},
                                           {"role": "user", "content": "你是谁"},
                                           {"role": "assistant",
                                            "content": "我是一个新能源大数据平台的数据分析专家，专门帮助用户理解和分析新能源汽车相关的数据和信息。以下是按照您要求的格式返回的答案：/n我是新能源大数据平台的数据分析专家，负责解答您关于新能源汽车相关的问题。/n**您可以前往下面以下模块获得进一步的行业信息**：/n**1. 全球新能源汽车销量总览**/n**2. 品牌销售情况概况**/n**3. 车型销售情况概况**/n**4. 汽车保有量状况**/n**5. 汽车充电桩分布**/n**6. 新能源汽车行业资讯**/n请随时告诉我您具体的问题，我将进一步协助您。"},
                                           {"role": "user",
                                            "content": "你的回答不符合我的要求，只用保留上面回答中的“/n我是新能源大数据平台的数据分析专家，负责解答您关于新能源汽车相关的问题。/n**您可以前往下面以下模块获得进一步的行业信息**：/n**1. 全球新能源汽车销量总览**/n**2. 品牌销售情况概况**/n**3. 车型销售情况概况**/n**4. 汽车保有量状况**/n**5. 汽车充电桩分布**/n**6. 新能源汽车行业资讯**/n请随时告诉我您具体的问题，我将进一步协助您。”部分即可"},
                                           {"role": "assistant", "content": "好的，我明白了，请告诉我您的问题"},
                                           {"role": "user", "content": f"{question}"},
                                       ],
                                       )
    answer = str(response.choices[0].message.content)
    print(answer)
    return {"message": answer}

@app.options("/analysis")
async def options_handler():
    return {"status": "ok"}

@app.post("/analysis")
async def getusing(request: ChatRequest):
    question = request.question
    print(question)
    client = ZhipuAI(api_key=your_api_key)  # 填写您自己的APIKey
    response = client.chat.completions.create(
        model="glm-4-0520",  # 填写需要调用的模型编码
        messages=[
            {"role": "user", "content":
                """我的新能源汽车大数据分析平台有一个根据用户问题做自然语言理解，动态使用功能函数的需求，我的功能函数包括：
                    1. BrandCard - 单个品牌的卡片，可以用于介绍单个品牌
                    2. BrandCardList - 一个品牌介绍的卡牌组，可以用于销量前几的品牌展示
                    3. ChargeMap - 充电桩地图
                    4. NewsList - 新能源新闻资讯
                    5. SalePredictYear - 全球新能源汽车销量未来一年预测
                    6. SalePredictMonth - 全球新能源汽车销量特定月份预测
                    7. TypeCard - 车型卡片，介绍特定车型
                    8. TypeCardList - 车型卡片组
                    请根据用户的问题生成一个包含上述函数是否使用的列表（0代表不使用，1代表使用）。例如，用户问题是“新能源汽车目前的发展如何，未来几个月的销量如何”，则返回[0,1,0,1,1,0,0,0]。"""},
            {"role": "assistant", "content": "当然，请告诉我用户的问题"},
            {"role": "user", "content": "新能源汽车目前的发展如何，未来几个月的销量如何"},
            {"role": "assistant", "content": "生成的函数使用列表为:[0,0,0,0,1,0,0,0]"},
            {"role": "user",
             "content": "对应关系做得很好，但格式不正确，请仅给我返回数组，不需要任何其他任何的文字描述，例如“[1,0,1,0,0,0,0,0]”"},
            {"role": "assistant", "content": "好的我明白了，我会只给您返回数组，请告诉我用户的问题"},
            {"role": "user", "content": f"{question}"}

        ],
    )
    print(response.choices[0].message.content)
    arr = json.loads(response.choices[0].message.content)
    return {"using": arr}

@app.post("/brand_card")
async def brand_card(request: ChatRequest):
    client = ZhipuAI(api_key=your_api_key)  # 使用环境变量或者配置文件代替明文APIKey
    response = await asyncio.to_thread(client.chat.completions.create,
                                       model="glm-4-0520",  # 填写需要调用的模型编码
                                       messages=[
                                           {"role": "user",
                                            "content": "假设你作为一个新能源品牌专家，请回答我的问题，请把回答控制在较短的篇幅内"},
                                           {"role": "assistant",
                                            "content": "好的，请告诉我用户的问题"},
                                           {"role": "user",
                                            "content": f"用户问题是：{request.question},请从财务状况、市场表现、技术创新等方面进行用户需求品牌的分析。"},
                                       ],
                                       )
    answer = str(response.choices[0].message.content)
    responseforbrand = await asyncio.to_thread(client.chat.completions.create,
                                               model="glm-4-0520",  # 填写需要调用的模型编码
                                               messages=[
                                                   {"role": "user",
                                                    "content": '''请根据我给你的文字段，提取出BrandCard函数的参数{brand:str},我需要这个参数向后端请求相应的品牌信息，
                                                    你可以参考下面的示例：
                                                    文字段：特斯拉（Tesla, Inc.）是一家总部位于美国加利福尼亚州的汽车和能源公司，成立于2003年。特斯拉以生产电动汽车、太阳能产品和能源储存设备而闻名。该公司的创始人之一是亿万富翁伊隆·马斯克（Elon Musk），他也是特斯拉的首席执行官。
                                                    返回值：特斯拉
                                                    你需要提取出品牌名称，并只给我品牌名这个字符串'''},
                                                   {"role": "assistant",
                                                    "content": "好的，请给我您需要分析的文字段"},
                                                   {"role": "user",
                                                    "content": f'{answer}'},
                                               ],
                                               )
    brand = str(responseforbrand.choices[0].message.content)
    print(brand)
    return {"content": answer,
            "brand": brand
            }


@app.post("/brand_card_list")
async def brand_card_list(request: ChatRequest):
    client = ZhipuAI(api_key=your_api_key)  # 使用环境变量或者配置文件代替明文APIKey
    response = await asyncio.to_thread(client.chat.completions.create,
                                       model="glm-4-0520",  # 填写需要调用的模型编码
                                       messages=[
                                           {"role": "user",
                                            "content": "假设你作为一个新能源品牌专家，请回答我的问题，请把回答控制在较短的篇幅内"},
                                           {"role": "assistant",
                                            "content": "好的，请告诉我用户的问题"},
                                           {"role": "user",
                                            "content": f"用户问题是：{request.question}，请根据用户的问题针对用户需求的品牌做简要分析。"},
                                       ],
                                       )
    answer = str(response.choices[0].message.content)
    print(answer)
    responseforbrandlist = await asyncio.to_thread(client.chat.completions.create,
                                                   model="glm-4-0520",  # 填写需要调用的模型编码
                                                   messages=[
                                                       {"role": "user",
                                                        "content": '''请根据我给你的文字段，提取BrandCardlist函数的参数brandlist:[],我需要这个参数向后端请求相应的品牌信息，
                                                        你可以参考下面的示例：
                                                        文字段：一些值得关注的新能源汽车公司包括特斯拉（Tesla）、Rivian Automotive、NIO和BYD。这些公司在电动汽车技术和可再生能源领域展现出独特的创新和发展潜力。
                                                        返回值：["特斯拉", "Rivian Automotive", "NIO","BYD"]
                                                        你需要提取出品牌名称列表，并以数组样式返回,回答中仅包含该数组'''},
                                                       {"role": "assistant",
                                                        "content": "好的，请给我您需要分析的文字段"},
                                                       {"role": "user",
                                                        "content": f'{answer}'},
                                                   ],
                                                   )
    brandlist = str(responseforbrandlist.choices[0].message.content)
    brandlist = json.loads(brandlist)
    print(brandlist)
    return {"content": answer,
            "brandlist": brandlist
            }


@app.post("/charge_map")
async def charge_map(request: ChatRequest):
    client = ZhipuAI(api_key=your_api_key)  # 使用环境变量或者配置文件代替明文APIKey
    response = await asyncio.to_thread(client.chat.completions.create,
                                       model="glm-4-0520",  # 填写需要调用的模型编码
                                       messages=[
                                           {"role": "user",
                                            "content": "假设你作为一个充电服务专家，请回答我的问题，请把回答控制在较短的篇幅内"},
                                           {"role": "assistant",
                                            "content": "当然，请告诉我用户的问题"},
                                           {"role": "user",
                                            "content": f"用户问题是：{request.question}，请根据用户对新能源充电桩的相关需求进行详细的分析。"},
                                       ],
                                       )
    answer = str(response.choices[0].message.content)
    print(answer)

    responseforcharge = await asyncio.to_thread(client.chat.completions.create,
                                                model="glm-4-0520",  # 填写需要调用的模型编码
                                                messages=[
                                                    {"role": "user",
                                                     "content": '''请根据我给你的文字段，提取出chargemap函数的参数{area:str},我需要这个参数向后端请求相应的地图位置信息，
                                                        你可以参考下面的示例：
                                                        文字段：中国的电动汽车充电桩建设在全球处于领先地位，涵盖慢充电桩、交流快充电桩和直流快充电桩，分布广泛覆盖城市、高速公路和商业区域，由国家级、地方级和企业级运营商共同构建充电网络。政府的支持政策推动了这一发展，然而仍需解决标准化、利用率和互联互通等挑战，以进一步完善电动车充电基础设施。
                                                        返回值：中国
                                                        你需要提取出地区，并只给我地区名这个字符串'''},
                                                    {"role": "assistant",
                                                     "content": "好的，请给我您需要分析的文字段"},
                                                    {"role": "user",
                                                     "content": f'{answer}'},
                                                ],
                                                )
    area = str(responseforcharge.choices[0].message.content)
    print(area)
    return {"content": answer,
            "area": area
            }


@app.post("/sale_predict_month")
async def sale_predict_month(request: ChatRequest):
    client = ZhipuAI(api_key=your_api_key)  # 使用环境变量或者配置文件代替明文APIKey
    response = await asyncio.to_thread(client.chat.completions.create,
                                       model="glm-4-0520",  # 填写需要调用的模型编码
                                       messages=[
                                           {"role": "user",
                                            "content": "假设你作为一个新能源汽车市场预测专家，请回答我的问题，请把回答控制在较短的篇幅内"},
                                           {"role": "assistant",
                                            "content": "当然，请告诉我用户希望了解的具体月份和相关预测内容。"},
                                           {"role": "user",
                                            "content": f"用户问题是：{request.question}，请结合用户问题和当前市场动态进行分析。"},
                                       ],
                                       )
    answer = str(response.choices[0].message.content)
    print(answer)
    responseformonth = await asyncio.to_thread(client.chat.completions.create,
                                               model="glm-4-0520",  # 填写需要调用的模型编码
                                               messages=[
                                                   {"role": "user",
                                                    "content": '''请根据我给你的文字段，提取出SalePredictMonth函数的参数month:int,我需要这个参数向后端请求相应的销量预测信息，
                                                            你可以参考下面的示例：
                                                            文字段：预测明年10月份，新能源汽车市场有望继续保持增长势头。未来的新能源汽车市场预计将呈现出多元化的发展趋势，产品线将更加丰富，涵盖不同类型和价格段的电动车型，以满足消费者多样化的需求。销量增长到300000，同比增长7.98%。新能源汽车市场的未来充满了机遇和挑战，需要行业各方共同努力，不断推动技术创新和市场发展，以实现可持续的、清洁的汽车出行愿景。
                                                            返回值：2025.10
                                                            你需要提取出具体的日期，并只给我日期这个数字，以上述格式返回'''},
                                                   {"role": "assistant",
                                                    "content": "好的，请给我您需要分析的文字段"},
                                                   {"role": "user",
                                                    "content": f'{answer}'},
                                               ],
                                               )
    month = str(responseformonth.choices[0].message.content)
    print(month)
    return {"content": answer,
            "month": month
            }


@app.post("/sale_predict_year")
async def sale_predict_year(request: ChatRequest):
    client = ZhipuAI(api_key=your_api_key)  # 使用环境变量或者配置文件代替明文APIKey
    response = await asyncio.to_thread(client.chat.completions.create,
                                       model="glm-4-0520",  # 填写需要调用的模型编码
                                       messages=[
                                           {"role": "user",
                                            "content": "假设你作为一个新能源汽车市场预测专家，请回答我的问题，请把回答控制在较短的篇幅内"},
                                           {"role": "assistant",
                                            "content": "当然，请告诉我用户希望了解的具体市场预测内容。"},
                                           {"role": "user",
                                            "content": f"用户问题是：{request.question}，请结合用户问题和当前市场趋势进行分析。"},
                                       ],
                                       )
    answer = str(response.choices[0].message.content)
    print(answer)
    return {"content": answer}


@app.post("/news_list")
async def news_list(request: ChatRequest):
    client = ZhipuAI(api_key=your_api_key)  # 使用环境变量或者配置文件代替明文APIKey
    response = await asyncio.to_thread(client.chat.completions.create,
                                       model="glm-4-0520",  # 填写需要调用的模型编码
                                       messages=[
                                           {"role": "user",
                                            "content": "假设你作为一个新能源新闻专家，请回答我的问题，请把回答控制在较短的篇幅内"},
                                           {"role": "assistant",
                                            "content": "当然，请告诉我用户想要了解的新闻类别或最新动态。"},
                                           {"role": "user",
                                            "content": f"用户问题是：{request.question}，请根据用户问题提供近期的行业动态分析。"},
                                       ],
                                       )
    answer = str(response.choices[0].message.content)
    print(answer)
    return {"content": answer}

# @app.post("/sales")
# async def saleana():
#     client = ZhipuAI(api_key=your_api_key)  # 使用环境变量或者配置文件代替明文APIKey
#     response = await asyncio.to_thread(client.chat.completions.create,
#                                        model="glm-4-0520",  # 填写需要调用的模型编码
#                                        messages=[
#                                            {"role": "user",
#                                             "content": "假设你作为一个新能源大数据平台的数据分析专家，请回答我的问题"},
#                                            {"role": "assistant",
#                                             "content": "当然，为了更精准的回答，请告诉我一些关于平台的信息和回答的具体格式要求"},
#                                            {"role": "user",
#                                             "content": "用户能从当前页面上看到全球新能源汽车的销量，同时看到销量增长的同比和环比，请根据这些内容，结合最新时讯，为新能源行业做一个大概的概括，为用户提供一些投资建议"},
#                                        ],
#                                        )
#     answer = str(response.choices[0].message.content)
#     print(answer)
#     return {"message": answer}
#
#
#
# @app.post("/brands")
# async def saleana(brand: str):
#     client = ZhipuAI(api_key=your_api_key)  # 使用环境变量或者配置文件代替明文APIKey
#     response = await asyncio.to_thread(client.chat.completions.create,
#                                        model="glm-4-0520",  # 填写需要调用的模型编码
#                                        messages=[
#                                            {"role": "user",
#                                             "content": "假设你作为一个新能源大数据平台的数据分析专家，请回答我的问题"},
#                                            {"role": "assistant",
#                                             "content": "当然，为了更精准的回答，请告诉我一些关于平台的信息和回答的具体格式要求"},
#                                            {"role": "user",
#                                             "content": f"用户能够从当前页面上看到全球新能源汽车的销量前五的品牌，以及销量品牌占比，根据这些内容，结合最新时讯，分析销量最高品牌{brand}的优劣势和布局"},
#                                        ],
#                                        )
#     answer = str(response.choices[0].message.content)
#     print(answer)
#     return {"message": answer}
#
#
# @app.post("/brandscompare")
# async def saleana(brand1: str, brand2: str):
#     client = ZhipuAI(api_key=your_api_key)  # 使用环境变量或者配置文件代替明文APIKey
#     response = await asyncio.to_thread(client.chat.completions.create,
#                                        model="glm-4-0520",  # 填写需要调用的模型编码
#                                        messages=[
#                                            {"role": "user",
#                                             "content": "假设你作为一个新能源大数据平台的数据分析专家，请回答我的问题"},
#                                            {"role": "assistant",
#                                             "content": "当然，为了更精准的回答，请告诉我一些关于平台的信息和回答的具体格式要求"},
#                                            {"role": "user",
#                                             "content": f"用户想要查看{brand1}和{brand2}的品牌对比分析，结合最新时讯，给我一个完善的分析报告"},
#                                        ],
#                                        )
#     answer = str(response.choices[0].message.content)
#     print(answer)
#     return {"message": answer}
#
#
# @app.post("/types")
# async def saleana():
#     client = ZhipuAI(api_key=your_api_key)  # 使用环境变量或者配置文件代替明文APIKey
#     response = await asyncio.to_thread(client.chat.completions.create,
#                                        model="glm-4-0520",  # 填写需要调用的模型编码
#                                        messages=[
#                                            {"role": "user",
#                                             "content": "假设你作为一个新能源大数据平台的数据分析专家，请回答我的问题"},
#                                            {"role": "assistant",
#                                             "content": "当然，为了更精准的回答，请告诉我一些关于平台的信息和回答的具体格式要求"},
#                                            {"role": "user",
#                                             "content": "用户能够从当前页面上看到全球新能源汽车的销量前五的车型，根据这些内容，结合最新时讯，分析这些车型的优劣势"},
#                                        ],
#                                        )
#     answer = str(response.choices[0].message.content)
#     print(answer)
#     return {"message": answer}
#
#
# @app.post("/typescompare")
# async def saleana(type1: str, type2: str):
#     client = ZhipuAI(api_key=your_api_key)  # 使用环境变量或者配置文件代替明文APIKey
#     response = await asyncio.to_thread(client.chat.completions.create,
#                                        model="glm-4-0520",  # 填写需要调用的模型编码
#                                        messages=[
#                                            {"role": "user",
#                                             "content": "假设你作为一个新能源大数据平台的数据分析专家，请回答我的问题"},
#                                            {"role": "assistant",
#                                             "content": "当然，为了更精准的回答，请告诉我一些关于平台的信息和回答的具体格式要求"},
#                                            {"role": "user",
#                                             "content": f"用户想要查看{type1}和{type2}的车型对比分析，结合最新时讯，给我一个完善的分析报告"},
#                                        ],
#                                        )
#     answer = str(response.choices[0].message.content)
#     print(answer)
#     return {"message": answer}
#
#
# @app.post("/quantity")
# async def saleana():
#     client = ZhipuAI(api_key=your_api_key)  # 使用环境变量或者配置文件代替明文APIKey
#     response = await asyncio.to_thread(client.chat.completions.create,
#                                        model="glm-4-0520",  # 填写需要调用的模型编码
#                                        messages=[
#                                            {"role": "user",
#                                             "content": "假设你作为一个新能源大数据平台的数据分析专家，请回答我的问题"},
#                                            {"role": "assistant",
#                                             "content": "当然，为了更精准的回答，请告诉我一些关于平台的信息和回答的具体格式要求"},
#                                            {"role": "user",
#                                             "content": f"结合最新时讯，给我一个完善中国新能源汽车保有量的分析报告"},
#                                        ],
#                                        )
#     answer = str(response.choices[0].message.content)
#     print(answer)
#     return {"message": answer}
#
#
# @app.post("/charge")
# async def saleana(type1: str, type2: str):
#     client = ZhipuAI(api_key=your_api_key)  # 使用环境变量或者配置文件代替明文APIKey
#     response = await asyncio.to_thread(client.chat.completions.create,
#                                        model="glm-4-0520",  # 填写需要调用的模型编码
#                                        messages=[
#                                            {"role": "user",
#                                             "content": "假设你作为一个新能源大数据平台的数据分析专家，请回答我的问题"},
#                                            {"role": "assistant",
#                                             "content": "当然，为了更精准的回答，请告诉我一些关于平台的信息和回答的具体格式要求"},
#                                            {"role": "user",
#                                             "content": f"结合最新时讯，给我一个中国电车充电桩的分析报告"},
#                                        ],
#                                        )
#     answer = str(response.choices[0].message.content)
#     print(answer)
#     return {"message": answer}
