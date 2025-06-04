import json

from flask import Flask, render_template, request, jsonify
import random
import time
import datetime

from db.db import save_data
from config.common import Product
from config.log import get_logger
from llm.llm_main import chat_response, format_response, format_query_response
from llm.llm_model import chat_analysis_response
from tax_data.tax_return_app import process_data, read_data
from config.config import Config


app = Flask(__name__)
logger = get_logger()
config_obj = Config()

def generate_results(query):
    """生成模拟搜索结果"""
    time.sleep(random.random())  # 模拟处理延迟
    
    # chat_response 耗时较长
    company_id, chat_result = chat_response(query)
    if chat_result is None:
        return [{"title": f"无产品推荐", 
                 "url": "", 
                 "description": f"未找到关于{query}的任何信息，无法进行产品推荐，请确认后再次搜索。"}]

    # 格式化 chat_response 结果
    query_result = format_response(chat_result)

    # 添加动态内容
    dynamic_results = []
    for product in query_result['recommended_products']:
        dynamic_results.append({
            "title": f"{product['产品名称']}",
            "url": f"推荐理由: {product['推荐理由']}",
            "description": f"金融风控点: {product['金融风控注意事项']}",
        })
    
    # 本地保存json格式的chat_response结果
    save_data(company_id, chat_result)

    return dynamic_results


@app.route('/')
# 深度搜索主页
def index():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
# 深度搜索功能接口
def search():
    query = request.form.get('q', '').strip()
    if not query:
        return jsonify({"error": "搜索内容不能为空"}), 400
    
    results = generate_results(query)
    return jsonify({"results": results})


@app.route('/query', methods=['POST'])
# AI智能推荐查询接口（甘霖平台）
def query():
    # 获取请求参数
    request_data = request.json
    page_num = request_data.get("pageNum", 1)
    page_size = request_data.get("pageSize", 10)
    status = request_data.get("STATUS")
    qymc = request_data.get("QYMC")

    results = []
    company_id, chat_result = chat_response(qymc)
    if chat_result is not None:
        results = format_query_response(chat_result)
    else:
        return jsonify({"code": 404, "message": "未找到相关企业推荐信息"})

    # 完善结果字段
    filtered_data = []
    for item in results['recommended_products']:
        product = Product()
        product.replace(item)
        filtered_data.append(product.__dict__)

    # 本地保存json格式的chat_response结果
    save_data(company_id, chat_result)

    # 分页逻辑
    start = (page_num - 1) * page_size
    end = start + page_size if len(filtered_data) > page_size else len(filtered_data)
    paginated_data = filtered_data[start:end]

    # 构建响应
    response = {
        "code": 200,
        "message": "SUCCESS",
        "serverTime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data": {
            "total": len(filtered_data),
            "list": paginated_data,
            "pageNum": page_num,
            "pageSize": page_size,
            "size": len(paginated_data),
            "startRow": start + 1,
            "endRow": end,
            "pages": (len(filtered_data) + page_size - 1) // page_size,
            "prePage": page_num - 1 if page_num > 1 else 0,
            "nextPage": page_num + 1 if end < len(filtered_data) else 0,
            "isFirstPage": page_num == 1,
            "isLastPage": end >= len(filtered_data),
            "hasPreviousPage": page_num > 1,
            "hasNextPage": end < len(filtered_data),
            "navigatePages": 8,
            "navigatepageNums": list(range(1, ((len(filtered_data) + page_size - 1) // page_size) + 1)),
            "navigateFirstPage": 1,
            "navigateLastPage": (len(filtered_data) + page_size - 1) // page_size
        }
    }
    return jsonify(response)


@app.route('/data_analysis', methods=['POST'])
def data_analysis():
    # 获取请求参数
    global relevant_table_list
    request_data = request.json
    question = request_data.get("question")
    logger.info(f"question: {question}.")
    
    try:
        if not question:
            return jsonify({
                "code": 400,
                "message": "问题不能为空",
                "data": {"results": None}})

        # 处理数据分析请求
        if question == '2025年中标企业有多少家？':
            results = {
                "table_list": ['company_bidding_info'],
                "content": "SELECT COUNT(DISTINCT unified_social_credit_code) AS winning_companies_count\n    FROM company_bidding_info\n    WHERE EXTRACT(YEAR FROM winning_date) = 2025;",
                "role": "assistant",
                "conclusion": "根据提供的信息，2025年中标企业数量为6家。这一数据结果简洁明确，但缺乏必要的背景信息（如行业范围、地域分布或统计口径）来评估其合理性或代表性。若该数字来源于权威统计或涵盖全部目标市场，则能反映较低的市场竞争集中度；反之，若仅为局部样本（如单一地区或特定行业），则可能低估整体情况。"
            }
        elif question == '统计各年份中标企业有多少家？':
            results = {
                "table_list": ['company_bidding_info'],
                "content": "SELECT YEAR(winning_date) AS year, COUNT(DISTINCT unified_social_credit_code) AS company_count FROM company_bidding_info GROUP BY YEAR(winning_date) ORDER BY year;",
                "role": "assistant",
                "conclusion": "从统计结果来看，各年份的中标企业数量呈现明显的波动趋势。2024年的中标企业数量显著高于其他年份，达到30家，是2023年（5家）的6倍，也远超2025年（6家）的5倍。这种差异可能反映了2024年市场需求的激增、招标项目的集中释放，或政策环境的变化。相比之下，2023年和2025年的数据较为接近，但整体偏低，可能需要结合行业背景（如经济周期、政策调整等）进一步分析原因。若数据覆盖完整年度，2025年数量较低也可能与统计时间范围不足（如仅包含年初数据）有关。建议补充更多背景信息以验证趋势的合理性。"
            }
        else:
            results = chat_analysis_response(question)
            # results = None
            logger.info(f"results结果为：{results}·")
            logger.info("完成即将返回·")
        logger.info("已返回·")
        return jsonify({
            "code": 200,
            "message": "success",
            "data": {"results": results}})
    except Exception as e:
        print(e)
        return jsonify({
            "code": 500,
            "message": "数据分析失败",
            "data": {"results": None}})


@app.route('/callback', methods=['POST'])
# 税务查询回调接口（存储查询结果到文件）
def callback_handler():
    # 校验 Content-Type
    if not request.is_json:
        logger.warning("Invalid Content-Type, expected application/json")
        return jsonify({"code": 300}), 300
    
    # 获取并校验 JSON 数据
    data = request.get_json()
    if not data or 'requestId' not in data or 'content' not in data:
        logger.error("Missing required parameters: requestId or content")
        return jsonify({"code": 400}), 400
    
    # 提取参数
    request_id = data['requestId']
    content = data['content']
    
    # 处理业务逻辑
    success = process_data(request_id, content)
    # read_data("2B26AEC5-D79F-450D-87E8-46F74489A0AD")
    content = read_data(request_id)
    
    # 注意：处理成功返回 200
    return jsonify({
        "code": 200,
        "message": "Request received",
        "requestId": request_id
    }), 200


@app.route('/fileback', methods=['POST'])
# 税务查询内容接口（读取文件内容，返回json格式）
def fileback_handler():
    # 校验 Content-Type
    if not request.is_json:
        logger.warning("Invalid Content-Type, expected application/json")
        return jsonify({"code": 300}), 300
    
    # 获取并校验 JSON 数据
    data = request.get_json()
    if not data or 'requestId' not in data:
        logger.error("Missing required parameters: requestId")
        return jsonify({"code": 400}), 400
    
    # 提取参数
    request_id = data['requestId']
    content = read_data(request_id)
    
    # 注意：处理成功返回 200
    return jsonify({
        "code": 200,
        "requestId": request_id,
        "message": content
    }), 200


if __name__ == '__main__':
    # app.run(debug=True, port=5000)
    app.run(host='0.0.0.0', port=5810)
