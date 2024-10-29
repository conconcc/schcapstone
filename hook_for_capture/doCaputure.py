import requests
import numpy as np
from dotenv import load_dotenv
from datetime import datetime, timedelta
from useCapture import *
from setFrame import *


# 프레임을 저장할 디렉토리 생성
save_dir = "../captured_frames"
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

for loc in location:
    cctv_type, lat, lng = loc
    cctv_data, file_create_time = get_cctv_url(cctv_type, lat, lng)

    if cctv_data:
        cctv_name = cctv_data['cctvname']
        cctv_url = cctv_data['cctvurl']

        # CCTV 정보 출력: 지역, 시간, URL을 한 줄에 출력
        print(f"{cctv_name} | {file_create_time} | {cctv_url}")

        with open('../result_file/cctv_string_data.txt', 'a', encoding='utf-8') as f:
            f.write(f'{cctv_name} {file_create_time} {cctv_url}\n\n')

        print("CCTV 정보가 cctv_string_data.txt 파일에 저장되었습니다.")

        # useCapture에서 가져와 해당 URL에서 프레임 캡처
        capture_frames(cctv_url, save_dir, duration=30, fps=2)

        print(f"{cctv_name}의 프레임 캡처가 완료되었습니다.")
        time.sleep(5)

    # 모든 캡처가 완료된 후, 프레임 삭제 여부 입력 받기
delete_choice = input("캡처한 프레임을 삭제하시겠습니까? (y/n): ").strip().lower()
if delete_choice == 'y':
    delete_frames(save_dir)
else:
    print("프레임이 삭제되지 않았습니다.")