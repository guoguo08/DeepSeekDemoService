from flask import Flask, request, jsonify
from config.log import get_logger
# import logging
import json
import os


app = Flask(__name__)

# 配置日志记录
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
logger = get_logger()

# 保存文件的目录
SAVE_DIR = "data"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)


def save_content_to_file(content, file_path):
    """
    将 content（字符串或字典）保存到本地文件
    :param content: 字符串或字典数据
    :param file_path: 文件路径
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        if isinstance(content, dict):
            # 如果是字典，保存为 JSON 格式
            json.dump(content, f, ensure_ascii=False, indent=4)
        elif isinstance(content, str):
            # 如果是字符串，直接写入文件
            f.write(content)
        else:
            raise ValueError("Unsupported content type")
    print(f"Content saved to {file_path}")


def read_content_from_file(file_path):
    """
    从本地文件读取 content（字符串或字典）
    :param file_path: 文件路径
    :return: 字符串或字典数据
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        try:
            # 尝试将内容解析为字典
            return json.loads(content)
        except json.JSONDecodeError:
            # 如果解析失败，返回原始字符串
            return content
    print(f"Content loaded from {file_path}")


def process_data(request_id, content):
    """
    处理业务数据的函数（需根据实际业务补充实现）
    例如：保存到数据库、发送消息队列等操作
    """
    try:
        # 示例处理逻辑 - 请替换为实际业务代码
        logger.info(f"Processing requestId: {request_id}")
        logger.info(f"Received content: {content}")

        # 判断 content 格式并保存到本地文件
        file_path = os.path.join(SAVE_DIR, f"{request_id}.json")
        save_content_to_file(content, file_path)

        return True
    except Exception as e:
        logger.error(f"Error processing data: {str(e)}")
        return False


def read_data(request_id):
    """
    读取业务数据的函数（需根据实际业务补充实现）
    例如：从数据库中查询数据
    """
    try:
        file_path = os.path.join(SAVE_DIR, f"{request_id}.json")
        if not os.path.exists(file_path):
            return jsonify({"error": "File not found"}), 404
        # 读取 content 文件
        content = read_content_from_file(file_path)
        logger.info(f"Reading content: {content}")
        return content
    except Exception as e:
        logger.error(f"Error reading data: {str(e)}")
        return None


@app.route('/callback', methods=['POST'])
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
    
    # 注意：无论处理成功与否都返回 200
    return jsonify({
        "code": 200,
        "message": "Request received",
        "requestId": request_id
    }), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5820, debug=False)  # 生产环境应设置 debug=False
