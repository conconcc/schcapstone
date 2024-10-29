import requests
import numpy as np
from dotenv import load_dotenv
from datetime import datetime, timedelta
from useCapture import *

load_dotenv()
api_key = os.getenv('data_api_key')


def get_cctv_url(cctv_type, lat, lng):
    start_time = datetime.now() - timedelta(minutes=3)
    formatted_time = start_time.strftime('%Y-%m-%d %H:%M:%S')

    minX = str(lng - 1)
    maxX = str(lng + 1)
    minY = str(lat - 1)
    maxY = str(lat + 1)

    api_calls = [
        'https://openapi.its.go.kr:9443/cctvInfo?' \
        'apiKey=' + api_key + \
        '&type=its&cctvType=2' \
        '&minX=' + minX + \
        '&maxX=' + maxX + \
        '&minY=' + minY + \
        '&maxY=' + maxY + \
        '&getType=json',

        'https://openapi.its.go.kr:9443/cctvInfo?' \
        'apiKey=7bc8224ed63b44ba8870f0d93bfc21a4' \
        f'&type={cctv_type}&cctvType=2' \
        '&minX=' + minX + \
        '&maxX=' + maxX + \
        '&minY=' + minY + \
        '&maxY=' + maxY + \
        '&getType=json'
    ]

    cctv_data = []
    for api_call in api_calls:
        w_dataset = requests.get(api_call).json()
        if 'response' not in w_dataset:
            continue

        data = w_dataset['response']['data']
        cctv_data.extend(data)

    if not cctv_data:
        print(f"{lat}, {lng} 좌표에서 CCTV 데이터가 없습니다.")  # 데이터가 없는 경우 확인

    coordx_list = []
    for index, data in enumerate(cctv_data):
        xy_couple = (float(cctv_data[index]['coordy']), float(cctv_data[index]['coordx']))
        coordx_list.append(xy_couple)

    coordx_list = np.array(coordx_list)
    leftbottom = np.array((lat, lng))
    distances = np.linalg.norm(coordx_list - leftbottom, axis=1)
    min_index = np.argmin(distances)

    return cctv_data[min_index], formatted_time


location = [
    ["its", 36.772996, 126.930613],
    ["ex", 38.2001, 128.5246],
    ["ex", 36.59149088, 126.5603431],
    ["ex", 36.25351408, 127.2799814]
]


