import cv2
import os
import time


def capture_frames(video_link, save_dir, duration=30, fps=2):
    """
    지정된 동영상 링크에서 프레임을 캡처하고 저장합니다.

    Args:
        video_link (str): 동영상 링크
        save_dir (str): 프레임 저장 디렉토리
        duration (int): 캡처 시간 (초)
        fps (int): 프레임 캡처 속도 (프레임/초)
    """
    print("캡처를 시작합니다.")

    # 저장 디렉토리 확인 및 생성
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    cap = cv2.VideoCapture(video_link)

    if not cap.isOpened():
        print(f"Error: Cannot open video stream at {video_link}")
        return

    # 캡처할 프레임 수를 계산합니다.
    total_frames = int(duration * fps)

    # 기존 파일 중 최대 숫자 찾기
    existing_files = [f for f in os.listdir(save_dir) if f.startswith("frame_") and f.endswith('.jpg')]
    frame_count = 0
    if existing_files:
        # 기존 파일에서 숫자 추출하여 최대값 찾기
        existing_numbers = [int(f.split('_')[-1].split('.')[0]) for f in existing_files]
        frame_count = max(existing_numbers) + 1  # 다음 숫자부터 시작

    # 프레임 캡처 루프
    for _ in range(total_frames):
        ret, frame = cap.read()

        if not ret:
            print("Error: Unable to read frame.")
            break

        # 프레임 저장
        file_path = os.path.join(save_dir, f"frame_{frame_count}.jpg")
        cv2.imwrite(file_path, frame)

        frame_count += 1
        time.sleep(1 / fps)  # FPS에 맞춰 대기

    cap.release()


def delete_frames(save_dir, delay=300):
    """
    지정된 디렉토리의 모든 프레임을 지정된 시간 (초) 후 삭제합니다.

    Args:
        save_dir (str): 프레임 저장 디렉토리
        delay (int): 삭제 지연 시간 (초)
    """
    print("캡처를 삭제합니다.")
    time.sleep(delay)

    # 디렉토리 내 모든 파일 삭제
    for filename in os.listdir(save_dir):
        os.remove(os.path.join(save_dir, filename))
    print("모든 프레임이 삭제되었습니다.")
