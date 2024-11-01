from flask import Flask, jsonify, render_template
import os
import re
from hook_for_capture.runCapture import start_capture
import threading

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def get_data():
    try:
        data_dir = os.path.join(os.path.dirname(__file__), 'data')  # 절대 경로 사용
        data_list = []

        for filename in os.listdir(data_dir):
            if filename.endswith('.txt'):
                    with open(os.path.join(data_dir, filename), 'r', encoding='utf-8') as file:
                        for line in file:  # 각 줄을 읽고
                            line = line.strip()  # 공백 제거
                            # 정규 표현식으로 항목을 분리
                            match = re.match(r'\[(.*?)\]\s+(.*?)\s+(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+(\S+)',
                                             line)
                            if match:  # 정규 표현식 매칭 성공 시
                                location = match.group(2)  # 괄호 안의 내용 (위치)
                                region = match.group(1)  # 괄호 밖의 내용 (지역)
                                time = match.group(3)  # 시간
                                URL = match.group(4)  # URL
                                # JSON 객체로 데이터 추가
                                data_list.append({'location': location, 'region': region, 'time': time, 'URL': URL})

        return jsonify(data_list)
    except Exception as e:
        print(f"Error processing data: {e}")
        return jsonify({"error": str(e)}), 500

def run_capture_once():
    """서버 시작 시 단 한 번 캡처 작업을 실행하는 함수."""
    try:
        start_capture()  # 캡처 함수 호출
    except Exception as e:
        print(f"Error during capture: {e}")

def is_main_process():
    # 서버 시작 시 단 한 번 캡처 작업 실행
    return os.environ.get('WERKZEUG_RUN_MAIN') == 'true'

if __name__ == '__main__':
    if is_main_process():
        capture_thread = threading.Thread(target=run_capture_once)
        capture_thread.start()  # 캡처 작업 스레드 시작

    # Flask 서버를 메인 스레드에서 실행
    try:
        app.run(debug=True, threaded=True)  # Flask 서버 실행
    except KeyboardInterrupt:
        print("Shutting down the server...")