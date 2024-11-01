import os
import time
import requests
import numpy as np
from dotenv import load_dotenv
import traceback
import re
from datetime import datetime, timedelta
from .useCapture import capture_frames, delete_frames

load_dotenv()
api_key = os.getenv('data_api_key')
data_file_path = os.path.abspath('../schcapstone/data/cctv_string_data.txt')

location = [
    ["its", 36.772996, 126.930613],
    ["ex", 38.2001, 128.5246],
    ["ex", 36.59149088, 126.5603431],
    ["ex", 36.25351408, 127.2799814]
]

def get_cctv_url(cctv_type, lat, lng):
    formatted_time = time.strftime('%Y-%m-%d %H:%M:%S')

    minX, maxX = str(lng - 1), str(lng + 1)
    minY, maxY = str(lat - 1), str(lat + 1)

    api_calls = [
        f'https://openapi.its.go.kr:9443/cctvInfo?apiKey={api_key}&type=its&cctvType=2&minX={minX}&maxX={maxX}&minY={minY}&maxY={maxY}&getType=json',
        f'https://openapi.its.go.kr:9443/cctvInfo?apiKey=7bc8224ed63b44ba8870f0d93bfc21a4&type={cctv_type}&cctvType=2&minX={minX}&maxX={maxX}&minY={minY}&maxY={maxY}&getType=json'
    ]

    cctv_data = []
    for api_call in api_calls:
        try:
            response = requests.get(api_call)
            response.raise_for_status()
            w_dataset = response.json()
            if 'response' in w_dataset:
                cctv_data.extend(w_dataset['response']['data'])
        except requests.exceptions.RequestException as e:
            print(f"API 호출 중 오류 발생: {e}")

    if not cctv_data:
        print(f"{lat}, {lng} 좌표에서 CCTV 데이터가 없습니다.")
        return None, formatted_time

    coordx_list = np.array([(float(data['coordy']), float(data['coordx'])) for data in cctv_data])
    leftbottom = np.array((lat, lng))
    distances = np.linalg.norm(coordx_list - leftbottom, axis=1)
    min_index = np.argmin(distances)

    return cctv_data[min_index], formatted_time


import re
from datetime import datetime


def parse_entry(entry):
    match = re.match(r'(\[.*?\])\s+(.*?)\s+(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+(\S+)', entry)
    if match:
        region = match.group(1)  # [국도21]
        location_name = match.group(2)  # 아산 순천향대삼거리
        time = match.group(3)
        url = match.group(4)
        return {'region': region, 'location': location_name, 'time': time, 'url': url}
    return None


def is_within_30_minutes(time1, time2):
    t1 = datetime.strptime(time1, '%Y-%m-%d %H:%M:%S')
    t2 = datetime.strptime(time2, '%Y-%m-%d %H:%M:%S')
    return abs(t1 - t2) <= timedelta(minutes=30)

def update_entries(existing_entries, new_entry):
    new_entry_parsed = parse_entry(new_entry)
    if not new_entry_parsed:
        return existing_entries  # 새 엔트리가 유효하지 않으면 기존 엔트리 반환

    updated_entries = []
    updated = False

    for entry in existing_entries:
        parsed_entry = parse_entry(entry)
        if parsed_entry:
            if (parsed_entry['region'] == new_entry_parsed['region'] and
                parsed_entry['location'] == new_entry_parsed['location']):
                if is_within_30_minutes(parsed_entry['time'], new_entry_parsed['time']):
                    # 30분 이내의 같은 위치 데이터는 삭제 (추가하지 않음)
                    updated = True
                else:
                    # 30분 이후의 데이터는 그대로 유지
                    updated_entries.append(entry)
            else:
                updated_entries.append(entry)
        else:
            updated_entries.append(entry)

    # 새 엔트리 추가
    updated_entries.append(new_entry)

    # 시간순으로 정렬
    updated_entries.sort(key=lambda x: datetime.strptime(parse_entry(x)['time'], '%Y-%m-%d %H:%M:%S'), reverse=True)

    return updated_entries

def start_capture():
    while True:
        try:
            save_dir = os.path.abspath("captured_frames")
            os.makedirs(save_dir, exist_ok=True)

            for loc in location:
                cctv_type, lat, lng = loc
                try:
                    cctv_data, file_create_time = get_cctv_url(cctv_type, lat, lng)
                    if cctv_data is None:
                        continue

                    cctv_name = cctv_data['cctvname']
                    cctv_url = cctv_data['cctvurl']

                    # CCTV 이름 파싱
                    match = re.match(r'(\[.*?\])\s+(.*)', cctv_name)
                    if match:
                        region, location_name = match.groups()
                    else:
                        region = '[Unknown]'
                        location_name = cctv_name

                    new_entry = f'{region} {location_name} {file_create_time} {cctv_url}'

                    # 파일 읽기
                    existing_entries = []
                    if os.path.exists(data_file_path):
                        with open(data_file_path, 'r', encoding='utf-8') as f:
                            existing_entries = [line.strip() for line in f.read().split('\n\n') if line.strip()]

                    # 기존 항목 업데이트
                    updated_entries = update_entries(existing_entries, new_entry)

                    # 파일에 쓰기 (업데이트된 전체 내용)
                    with open(data_file_path, 'w', encoding='utf-8') as f:
                        f.write('\n\n'.join(updated_entries) + '\n\n')

                    print(f"{region} {location_name}의 정보가 업데이트되었습니다.")

                    capture_frames(cctv_url, save_dir, duration=30, fps=2)
                    time.sleep(1)

                except Exception as e:
                    print(f"CCTV 데이터 처리 중 오류 발생 (무시됨): {e}")
                    traceback.print_exc()

            # 사진 파일 관리
            if manage_captured_frames(save_dir):
                delete_frames(save_dir)

            print("모든 CCTV 데이터 처리 완료. 다시 시작합니다.")

        except Exception as e:
            print(f"프로그램 실행 중 심각한 오류 발생: {e}")
            traceback.print_exc()
            print("1분 후 다시 시작합니다.")
            time.sleep(60)  # 1분 대기 후 재시도


def manage_captured_frames(save_dir):
    files = [f for f in os.listdir(save_dir) if f.endswith('.jpg')]
    if not files:
        return False
    max_frame = max(int(f.split('_')[-1].split('.')[0]) for f in files)
    return max_frame >= 5120



if __name__ == "__main__":
    start_capture()