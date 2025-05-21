// c:/Users/didxo/OneDrive/Desktop/3rd project code(flask)/my-react-app/src/app/analysis.jsx
import React from "react";
// Ensure this path is correct for your project structure
import "./styles/analysis.css";
// assets 폴더가 'app' 폴더의 한 단계 위, 즉 'src/assets/'에 있다고 가정합니다.
// 만약 asset 폴더가 styles 폴더 안에 있다면 아래 경로가 맞을 수 있습니다.
// 실제 프로젝트 구조에 맞게 경로를 확인하고 수정해주세요.
import logoImage from "./styles/asset/logo.svg"; // 로고 이미지 경로
import copyIconPath1 from "./styles/asset/copy1.svg"; // 복사 아이콘으로 사용
import copyIconPath2 from "./styles/asset/copy2.svg"; // 복사 아이콘의 두 번째 부분으로 사용
import evaluationIconPath from "./styles/asset/evaluation_button.svg"; // 평가 아이콘으로 사용 (느낌표 모양 아이콘으로 교체 필요)
// import videoThumbnailPath from '../assets/images/video_thumbnail.jpg'; // 예시 경로
import { Component as EvaluationContent } from "./evaluate"; // evaluate.jsx의 컴포넌트를 가져옵니다.
// props가 제공되지 않을 경우 사용될 기본 플레이스홀더 데이터
const defaultAnalysisResult = {
	videoThumbnail:
		"https://via.placeholder.com/361x232.png?text=Video+Thumbnail",
	score: 0,
	exerciseCount: 0,
	feedbackQuote: "운동 분석 결과를 기다리고 있습니다...",
	detailedFeedback: "운동 영상이 분석되면 여기에 AI 피드백이 표시됩니다.",
	// import된 에셋 변수 사용
	// copyIcon은 이제 JSX에서 직접 copyIconPath1과 copyIconPath2를 사용합니다.
	// evaluationIcon: evaluationIconPath, // 여기에 느낌표 아이콘 경로를 할당해야 합니다.
};

const AnalysisPage = ({ analysisData }) => {
	// 전달된 analysisData를 사용하거나, 없을 경우 defaultAnalysisResult를 사용
	const currentAnalysis = analysisData || defaultAnalysisResult;

	// 평가 기준 아이콘 경로 (기본값 또는 props에서 받을 경우 사용)
	// 만약 analysisData에 evaluationIcon이 있다면 그것을 사용
	const evaluationIconSrc = analysisData?.evaluationIcon || evaluationIconPath;

	// 모달 상태 관리
	const [isModalOpen, setIsModalOpen] = React.useState(false);
	const openModal = () => setIsModalOpen(true);
	const closeModal = () => setIsModalOpen(false); // 오타 수정: setIsModal -> setIsModalOpen

	// 클립보드 복사 더미 함수
	const handleCopyFeedback = () => {
		navigator.clipboard
			.writeText(currentAnalysis.detailedFeedback)
			.then(() => alert("피드백이 복사되었습니다!"))
			.catch((err) => console.error("피드백 복사 실패:", err));
	};

	const handleEvaluationClick = () => {
		// alert("평가 기준 모달 열기 기능 구현 예정"); // 기존 alert 제거
		openModal(); // 모달 열기 함수 호출
	};

	return (
		<div className="analysis">
			<div className="overlap-wrapper">
				<header className="analysis-page-header">
					<div className="logo"></div>{" "}
				</header>

				{/* 메인 콘텐츠 스크롤 영역 */}
				<main className="analysis-content-area">
					<div className="analysis-video-container">
						<img
							className="analysis-video"
							alt="분석된 운동 영상"
							src={currentAnalysis.videoThumbnail}
						/>
					</div>

					{/* === NEW EXERCISE SUMMARY CARD === */}
					<div className="exercise-summary-card">
						<div className="summary-top-row">
							<div className="summary-score-box">
								<span className="score-value">{currentAnalysis.score}</span>
								<span className="score-unit">점</span>
							</div>
							<div className="summary-count-box">
								<span className="count-box-label">운동 결과</span>
								<p className="count-box-text">
									이번 운동으로 <span>{currentAnalysis.exerciseCount}</span>회
									했어요!
								</p>
							</div>
						</div>
						<div className="summary-feedback-quote">
							<p>"{currentAnalysis.feedbackQuote}"</p>
						</div>
					</div>
					{/* === END OF NEW EXERCISE SUMMARY CARD === */}

					{/* 평가 기준 버튼 영역 - 피드백 박스 바로 위, 우측 정렬 */}
					<div
						className="evaluation-button-area"
						onClick={handleEvaluationClick}
					>
						<img
							className="evaluation-icon"
							alt="평가 기준" // 이 alt 텍스트는 느낌표 아이콘에 맞게 "정보" 등으로 변경 가능
							src={evaluationIconSrc} // 이 src가 느낌표 아이콘을 가리켜야 함
						/>
						<span className="text-wrapper-8">평가기준</span>
					</div>

					{/* 피드백 섹션 */}
					<div className="feedback-container">
						<span className="feedback-label">피드백</span>{" "}
						{/* 피드백 라벨 추가 */}
						<p className="feedback-text">{currentAnalysis.detailedFeedback}</p>
						{/* 아이콘 2개를 합치기 위한 컨테이너 */}
						<div
							className="copy-icon-wrapper"
							alt="피드백 복사"
							onClick={handleCopyFeedback}
							role="button" // 클릭 가능한 요소임을 명시
							tabIndex={0} // 키보드 접근성 위해 추가
						>
							<img src={copyIconPath1} alt="" className="copy-icon-base" />
							<img src={copyIconPath2} alt="" className="copy-icon-overlay" />
						</div>
					</div>
				</main>

				{/* 평가 기준 모달 (isModalOpen 상태에 따라 표시) */}
				{isModalOpen && (
					<div className="evaluation-modal-overlay" onClick={closeModal}>
						<div
							className="evaluation-modal-content"
							onClick={(e) => e.stopPropagation()}
						>
							<button className="close-modal-button" onClick={closeModal}>
								&times;
							</button>
							<h2>운동 자세 평가 기준</h2>
							<p>
								스쿼트: 무릎이 발끝을 과도하게 넘지 않도록 주의합니다. 허리는
								곧게 펴고, 엉덩이는 충분히 내려가야 합니다.
							</p>
							<p>
								플랭크: 몸이 머리부터 발끝까지 일직선을 유지해야 합니다. 복근에
								힘을 주고 엉덩이가 처지거나 너무 올라가지 않도록 합니다.
							</p>
						</div>
					</div>
				)}
			</div>
		</div>
	);
};

export default AnalysisPage;
