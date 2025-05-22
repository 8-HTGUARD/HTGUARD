import cv2
import mediapipe as mp
import numpy as np
import os
import yt_dlp
import time
from PIL import Image, ImageFont, ImageDraw
from collections import deque
import pyttsx3
import threading
import queue

import subprocess

mp_pose = mp.solutions.pose

# 1) URL 변환 함수
def convert_shorts_to_watch(url):
    if "youtube.com/shorts/" in url:
        vid = url.split("/shorts/")[1].split("?")[0]
        return f"https://www.youtube.com/watch?v={vid}"
    return url

# 2) Mediapipe & 임계값 설정
mp_pose    = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
INIT_HEAD_MIN, INIT_HEAD_MAX   = 140, 180
INIT_ELBOW_MIN, INIT_ELBOW_MAX =  75, 115
HEAD_MIN_ANGLE, HEAD_MAX_ANGLE   = INIT_HEAD_MIN, INIT_HEAD_MAX
ELBOW_MIN_ANGLE, ELBOW_MAX_ANGLE = INIT_ELBOW_MIN, INIT_ELBOW_MAX

# 3) 이동평균 윈도우 (3D smoothing)
HIP_WINDOW   = deque(maxlen=5)
HEAD_WINDOW  = deque(maxlen=5)
ELBOW_WINDOW = deque(maxlen=5)

# 4) 타이머 상태
holding      = False
last_start   = None
elapsed_time = 0.0
last_msg     = None

# 5) 폰트 & TTS 엔진 + 큐/스레드
FONT_PATH = os.path.join(os.path.dirname(__file__), "../fonts/NotoSansKR-VariableFont_wght.ttf")
font = ImageFont.truetype(FONT_PATH, 32)


tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 150)
tts_queue  = queue.Queue()

def tts_worker():
    while True:
        text = tts_queue.get()
        tts_engine.say(text)
        tts_engine.runAndWait()
        tts_queue.task_done()

threading.Thread(target=tts_worker, daemon=True).start()

# 6) 3D 각도 계산
def calculate_angle_3d(a, b, c):
    ba = a - b
    bc = c - b
    cos_val = np.dot(ba, bc) / (np.linalg.norm(ba)*np.linalg.norm(bc) + 1e-6)
    return np.degrees(np.arccos(np.clip(cos_val, -1.0, 1.0)))

# 7) 텍스트 외곽선 그리기
def draw_text_with_outline(draw, text, position, font,
                           text_fill=(255,255,255), outline_fill=(0,0,0)):
    x,y = position
    for dx,dy in [(-2,-2),(2,-2),(-2,2),(2,2)]:
        draw.text((x+dx,y+dy), text, font=font, fill=outline_fill)
    draw.text((x,y), text, font=font, fill=text_fill)

# 8) 프레임 처리
def process_frame_plank(frame, results):
    global holding, last_start, elapsed_time, last_msg

    msg = "좋아요 "
    smooth_hip = smooth_head = smooth_elbow = 0.0

    if results.pose_world_landmarks and results.pose_landmarks:
        # 2D 힙 위치 기준선
        lm2 = results.pose_landmarks.landmark
        def get2(idx): return np.array([lm2[idx].x, lm2[idx].y], dtype=float)
        sh_y   = (get2(mp_pose.PoseLandmark.LEFT_SHOULDER)[1] +
                  get2(mp_pose.PoseLandmark.RIGHT_SHOULDER)[1]) / 2
        knee_y = (get2(mp_pose.PoseLandmark.LEFT_KNEE)[1] +
                  get2(mp_pose.PoseLandmark.RIGHT_KNEE)[1]) / 2
        hip_y  = (get2(mp_pose.PoseLandmark.LEFT_HIP)[1] +
                  get2(mp_pose.PoseLandmark.RIGHT_HIP)[1]) / 2
        ref_y  = (sh_y + knee_y) / 2
        THRESH = 0.05

        # 3D 각도 계산
        lm3 = results.pose_world_landmarks.landmark
        def get3(idx): return np.array([lm3[idx].x, lm3[idx].y, lm3[idx].z], dtype=float)
        hip_l = calculate_angle_3d(get3(mp_pose.PoseLandmark.LEFT_SHOULDER),
                                   get3(mp_pose.PoseLandmark.LEFT_HIP),
                                   get3(mp_pose.PoseLandmark.LEFT_KNEE))
        hip_r = calculate_angle_3d(get3(mp_pose.PoseLandmark.RIGHT_SHOULDER),
                                   get3(mp_pose.PoseLandmark.RIGHT_HIP),
                                   get3(mp_pose.PoseLandmark.RIGHT_KNEE))
        hip_a = (hip_l + hip_r) / 2
        ear3   = get3(mp_pose.PoseLandmark.LEFT_EAR)
        mid_sh = (get3(mp_pose.PoseLandmark.LEFT_SHOULDER) +
                  get3(mp_pose.PoseLandmark.RIGHT_SHOULDER)) / 2
        mid_hip= (get3(mp_pose.PoseLandmark.LEFT_HIP) +
                  get3(mp_pose.PoseLandmark.RIGHT_HIP)) / 2
        head_a  = calculate_angle_3d(ear3, mid_sh, mid_hip)
        elbow_a = calculate_angle_3d(get3(mp_pose.PoseLandmark.LEFT_ELBOW),
                                     mid_sh, mid_hip)

        # smoothing
        HIP_WINDOW.append(hip_a)
        HEAD_WINDOW.append(head_a)
        ELBOW_WINDOW.append(elbow_a)
        smooth_hip, smooth_head, smooth_elbow = (
            np.mean(HIP_WINDOW), np.mean(HEAD_WINDOW), np.mean(ELBOW_WINDOW)
        )

        # 힙 피드백 (2D 기준선)
        if hip_y > ref_y + THRESH:
            msg = "엉덩이가 너무 내려갔어요.올려주세요"
        elif hip_y < ref_y - THRESH:
            msg = "엉덩이가 너무 올라갔어요. 내려주세요"
        # 헤드
        elif not (HEAD_MIN_ANGLE <= smooth_head <= HEAD_MAX_ANGLE):
            msg = "시선을 바닥 30cm 앞에 두세요"
        # 엘보
        elif not (ELBOW_MIN_ANGLE <= smooth_elbow <= ELBOW_MAX_ANGLE):
            msg = "팔꿈치를 어깨 바로 아래에 두세요"
    else:
        msg = "사람이 화면에 보여야 합니다"

    # 음성 큐에 넣기
    if msg != last_msg:
        tts_queue.put(msg)
        last_msg = msg

    # 타이머
    now = time.time()
    if msg == "좋아요 ":
        if not holding:
            holding, last_start = True, now
    else:
        if holding:
            elapsed_time += now - last_start
            holding = False
    display_time = elapsed_time + (now - last_start if holding else 0)

    # 랜드마크 & 그리기
    mp_drawing.draw_landmarks(frame, results.pose_landmarks,
                              mp_pose.POSE_CONNECTIONS)
    pil = Image.fromarray(frame)
    draw = ImageDraw.Draw(pil)
    draw_text_with_outline(draw,
        f"Hip: {int(smooth_hip)}°  Head: {int(smooth_head)}°  Elbow: {int(smooth_elbow)}°",
        (10,10), font)
    draw_text_with_outline(draw, msg, (10,60), font,
                           text_fill=(50,205,50))
    draw_text_with_outline(
        draw, f"Hold Time: {int(display_time)} s", (10,110), font,
        text_fill=(30,144,255)
    )
    return cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)

# 10) 유튜브 다운로드
def download_youtube_video(url, output_path="downloads"):
    opts = {
        'outtmpl': f'{output_path}/%(id)s.%(ext)s',
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4'
    }
    os.makedirs(output_path, exist_ok=True)
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

# 11) 분석 & 재생
def analyze_video(video_path):
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
    if not cap.isOpened():
        print("비디오 파일 열기 실패"); return
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    delay = int(1000/fps)
    pose = mp_pose.Pose(min_detection_confidence=0.5,
                        min_tracking_confidence=0.5)
    cv2.namedWindow("Plank Timer", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Plank Timer", 640, 480)
    while True:
        ret, frame = cap.read()
        if not ret: break
        results = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        out = process_frame_plank(frame, results)
        cv2.imshow("Plank Timer", out)
        if cv2.waitKey(delay) & 0xFF in (27, ord('q')): break
    total = int(elapsed_time + (time.time()-last_start)
                ) if (holding and last_start) else int(elapsed_time)
    print(f"최종 누적 시간: {total} 초")
    pose.close(); cap.release(); cv2.destroyAllWindows()

# 12) 메인
if __name__ == "__main__":
    url   = convert_shorts_to_watch(input("유튜브 링크 입력: ").strip())
    video = download_youtube_video(url)
    print(f"다운로드 완료: {video}")
    analyze_video(video)

def reencode_with_ffmpeg(input_path):
    temp_path = input_path.replace(".mp4", "_fixed.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-i", input_path,
        "-vcodec", "libx264", "-acodec", "aac",
        temp_path
    ])
    os.replace(temp_path, input_path)

def analyze_video_and_save(video_path, output_path):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 또는 *'H264' 도 시도 가능
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    if not out.isOpened():
        print("🚨 VideoWriter 저장 실패: 경로 또는 코덱 문제")

    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            print(f"🚨 프레임 읽기 실패! 현재까지 저장한 프레임 수: {frame_count}")
            break

        results = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        out_frame = process_frame_plank(frame, results)
        out_frame = cv2.resize(out_frame, (width, height))

        out.write(out_frame)
        frame_count += 1

    cap.release()
    out.release()
    pose.close()

    # 🔁 ffmpeg 재인코딩
    reencode_with_ffmpeg(output_path)

    file_size = os.path.getsize(output_path)
    print(f"📂 최종 저장된 파일 크기: {file_size / 1024:.2f} KB")
    print(f"✅ 총 저장된 프레임 수: {frame_count}")

    return output_path