from flask import Flask, render_template, request, jsonify
import random
import time
import datetime

from db.db import save_data
from config.common import Product
from llm.llm_main import chat_response, format_response, format_query_response


app = Flask(__name__)


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
def index():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('q', '').strip()
    if not query:
        return jsonify({"error": "搜索内容不能为空"}), 400
    
    results = generate_results(query)
    return jsonify({"results": results})


@app.route('/query', methods=['POST'])
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


if __name__ == '__main__':
    # app.run(debug=True, port=5000)
    app.run(host='0.0.0.0', port=5810)
