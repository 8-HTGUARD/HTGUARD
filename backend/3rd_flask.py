from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

# Flask 애플리케이션 객체 생성
app = Flask(__name__)
# CORS 활성화: React 앱과의 통신 문제 해결
CORS(app)

# 메인 페이지 라우트 정의
@app.route('/')
def main():
    """메인 페이지 요청 처리 함수"""
    return "메인 페이지입니다." # 실제 앱에서는 HTML 템플릿을 렌더링할 수 있습니다.

# 챗봇 페이지 라우트 정의
@app.route('/chatbot')
def chatbot():
    """챗봇 페이지 요청 처리 함수"""
    return "챗봇 페이지입니다." # 실제 앱에서는 챗봇 UI를 렌더링하거나 API 엔드포인트를 제공할 수 있습니다.

# 분석 페이지 라우트 정의 (POST 요청 처리)
@app.route('/analyze', methods=['POST'])
def analyze():
    """
    파일 업로드 및 분석 요청 처리 함수
    POST 요청을 받아서 업로드된 파일을 처리하고 분석 결과를 JSON 형태로 반환합니다.
    """
    # 요청에 파일이 없는 경우 에러 처리
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400 # 400 Bad Request

    file = request.files['file']

    # 파일이 선택되지 않은 경우 에러 처리
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400 # 400 Bad Request

    # 파일이 존재하는 경우
    if file:
        # 파일 저장 또는 분석 로직 구현 (현재는 최소 기능만 구현)
        # 실제 구현에서는 업로드된 파일을 저장하거나 분석하는 코드가 들어갑니다.
        # 예시:
        # from werkzeug.utils import secure_filename
        # filename = secure_filename(file.filename)
        # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # 임시 분석 결과 (실제 분석 결과로 대체해야 함)
        analysis_result = {"result": "파일 분석 완료 (결과는 추후 구현)"}
        return jsonify(analysis_result) # 분석 결과를 JSON 형태로 반환

    # 그 외의 오류 발생 시
    return jsonify({'error': 'Something went wrong'}), 500 # 500 Internal Server Error

# Flask 개발 서버 실행
if __name__ == '__main__':
    app.run(debug=True) # debug=True는 개발 모드로, 코드 변경 시 자동 재시작 및 디버깅 정보 제공