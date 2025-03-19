import json
import requests

from tax_data.tax_return_app import process_data


def get_file(data = {}):
    # 接口 URL
    url = "http://139.170.138.90:25810/fileback"  # 替换为实际的接口地址

    # 设置请求头
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "Accept": "application/json"
    }

    # 发送 POST 请求
    response = requests.request("POST", url, headers=headers, 
                                data=json.dumps(data).encode('utf-8'))
    process_data(response.json()['requestId'], response.json()['message'])
    return response.json()


if __name__=="__main__":
    data = {"requestId": "91D9A56A-4936-4F3D-9809-214AED398194"}
    content = get_file(data)['message']
    print(content)

    content.keys()
    '''
    ['lrbxxList', 'nsrsbh', 'qsggList', 'qyxxList', 
     'sbxxList', 'wfxwList', 'zcfzbxxList', 'zsxxList']
    '''
