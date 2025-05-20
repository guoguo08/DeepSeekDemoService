import time
import uuid
import json
import requests
import hashlib


def search_data(body = {}):
    # 接口 URL
    url = "http://open.caifbigdata.com/api/tax/queryTaxBill?v=1"  # 替换为实际的接口地址
    app_key = "Lb5UarxbLVa7HhHY"
    app_secret = "vjc5NeGJZs8La9J5zZA7mV39"
    version = "1"
    
    # UUID大写
    ticket_uuid = str(uuid.uuid4()).upper()

    # 获取当前时间戳（秒）
    timestamp_seconds = time.time()
    # 转换为毫秒级时间戳
    timestamp_milliseconds = int(timestamp_seconds * 1000)

    # sign MD5加密
    sign_str = (
        f"appKey={app_key}&"
        f"appSecret={app_secret}&"
        f"ticket={ticket_uuid}&"
        f"timestamp={timestamp_milliseconds}&"
        f"version={version}"
    )
    sign = hashlib.md5(sign_str.encode()).hexdigest().upper()

    # 请求参数
    data = {
        "appKey": app_key,
        "body": body,
        "sign": sign,
        "ticket": ticket_uuid,
        "timestamp": timestamp_milliseconds,
        "version": version
        }
    print(data)

    # 设置请求头
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "Accept": "application/json"
    }

    # 发送 POST 请求
    response = requests.request("POST", url, headers=headers, 
                                data=json.dumps(data).encode('utf-8'))
    print(response.json())
    return response.json()


if __name__=="__main__":
    body = {
        "requestId": str(uuid.uuid4()).upper(), 
        "creditCode": "91440300MAD2KJ3J8Q",
        "enterpriseName": "深圳市深度国际数据科技有限公司",
        "authType": 2,
        "callBackUrl": "http://139.170.138.90:25810/callback"}
    response = search_data({"requestId": str(uuid.uuid4()).upper()})
    # response = search_data(body)
    print(response)


    '''
    # 深圳市深度国际数据科技有限公司
    # 提交requestId: 91D9A56A-4936-4F3D-9809-214AED398194
    # 响应requestId: 187d3cfe-d794-45c6-b969-1bda8d96da84
    
    {'appKey': 'Lb5UarxbLVa7HhHY',
    'body': {'msg': 'SUCCESS',
    'code': 0,
    'data': {'requestId': '187d3cfe-d794-45c6-b969-1bda8d96da84',
    'resultCode': 1,
    'message': '提交成功'}},
    'sign': 'AFBE5AAECD6A9B2C9AE1BA359FEE1DAE',
    'ticket': '6E652BDD-3EF6-4FD1-B737-AEA63025AA44',
    'timestamp': 1741317126489,
    'version': 1}
    '''
