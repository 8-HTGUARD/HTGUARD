from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from flask_cors import CORS
import os
import threading

# 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
RESULT_FOLDER = os.path.join(BASE_DIR, 'results', 'processed')

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER

# 분석 함수 (YOLO, MediaPipe 등)
def analyze_background(input_path, output_path):
    from detector.plank import analyze_video_and_save
    analyze_video_and_save(input_path, output_path)

# 업로드 API
@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({"error": "video 파일이 전송되지 않았습니다."}), 400

    file = request.files['video']
    if file.filename == '':
        return jsonify({"error": "파일 이름이 비어 있습니다."}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    output_filename = f"processed_{filename}"
    output_path = os.path.join(app.config['RESULT_FOLDER'], output_filename)

    # 분석 백그라운드 시작
    threading.Thread(target=analyze_background, args=(filepath, output_path)).start()

    # React에서 분석된 영상 경로를 받을 수 있도록 처리
    return jsonify({
        "message": "분석 시작",
        "processed_video": f"/result_video/{output_filename}"  # 이 경로로 video 태그 연결 가능
    })

# 분석 결과 영상 제공
@app.route('/result_video/<filename>')
def get_result_video(filename):
    return send_from_directory(
        app.config['RESULT_FOLDER'],
        filename,
        as_attachment=False,
        mimetype='video/mp4'
    )

# 서버 실행
if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)
    app.run(debug=True)
