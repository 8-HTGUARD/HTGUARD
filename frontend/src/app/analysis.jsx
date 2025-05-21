import React, { useState, useEffect } from "react";

// 이미지 import 추가 (경로는 실제 파일 위치에 맞게 수정해주세요)

import analysisCopy1 from "./styles/asset/copy1.svg";
import analysisCopy2 from "./styles/asset/copy2.svg";
import analysisWifi from "./styles/asset/wifi.svg";
import analysisCellular from "./styles/asset/cellular.svg";
import analysisBattery from "./styles/asset/battery.svg";
import analysisTime from "./styles/asset/time.svg";
import analysisVideo from "./styles/asset/analysis_video.svg";
import analysisEvaluationButton from "./styles/asset/evaluation_button.svg";
// Assuming navigation icons are also in ./asset/ and are consistent with other components
import vectorWrapper from "./styles/asset/vector-wrapper.svg"; // For Home icon
import vector4 from "./styles/asset/Vector-4.svg"; // For Chatbot icon (used for 'image' variable)
import vector5 from "./styles/asset/Vector-5.svg"; // For Analysis icon (used for 'vector2' variable)

export const Analysis = ({ navigateTo = () => {}, videoPath = "" }) => {
  // 평가 기준 모달 상태
  const [showEvaluationModal, setShowEvaluationModal] = useState(false);

  // 평가 기준 모달 토글 함수
  const toggleEvaluationModal = () => {
    setShowEvaluationModal(!showEvaluationModal);
  };

  // Yolo 모델로부터 받아올 데이터 상태
  const [exerciseData, setExerciseData] = useState({
    score: 0,
    time: 0, // 운동 시간 (초)
    count: 0, // 운동 횟수
    feedback: "",
  });

  // Yolo 모델로부터 데이터를 받아오는 함수 (가정)
  const fetchYoloData = async () => {
    try {
      // 실제 API 엔드포인트로 변경해야 합니다.
      const response = await fetch("/api/yolo/results");
      const data = await response.json();

      // 받아온 데이터로 상태 업데이트
      setExerciseData({
        score: data.score || 0,
        time: data.time || 0,
        count: data.count || 0,
        feedback: data.feedback || "아직 분석 결과가 없습니다.",
      });
    } catch (error) {
      console.error("Yolo 데이터 fetching 오류:", error);
      setExerciseData((prevData) => ({
        ...prevData,
        feedback: "데이터를 불러오는 데 실패했습니다.",
      }));
    }
  };

  // 컴포넌트가 마운트될 때 Yolo 데이터 fetching 시작 (예시: 5초마다)
  useEffect(() => {
    // 실제로는 이벤트 기반 또는 필요에 따라 호출될 수 있습니다.
    const intervalId = setInterval(fetchYoloData, 5000);

    // 컴포넌트가 언마운트될 때 interval 정리
    return () => clearInterval(intervalId);
  }, []);

  // 운동 시간을 분:초 형식으로 변환하는 함수 (현재 사용되지 않음)
  const formatTime = (totalSeconds) => {
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${minutes}:${seconds < 10 ? "0" : ""}${seconds}`;
  };

  return (
    <div className="analysis">
      <div className="overlap-wrapper">
        <div className="overlap">
          <div className="analysis-feedback">
            <div className="overlap-group">
              <img
                className="analysis-copy"
                alt="Analysis copy"
                src={analysisCopy2} // Use analysisCopy2 as it was last in CSS
              />
            </div>
          </div>

          <div className="analysis-body" />

          <div className="title">HT GUARD</div>

          <img className="wifi" alt="Wifi" src={analysisWifi} />

          <div className="text-wrapper">카테고리</div>

          <img className="cellular" alt="Cellular" src={analysisCellular} />

          <img className="battery" alt="Battery" src={analysisBattery} />

          <img className="time" alt="Time" src={analysisTime} />

          <video
            className="analysis-video"
            width="800"
            height="450"
            controls
            src={`http://localhost:5000${videoPath}`}
          >
            영상 지원되지 않는 브라우저입니다.
          </video>

          <div className="analysis-score">
            <div className="div">
              <div
                className="score"
                style={{
                  width: `${exerciseData.score}%`,
                  background:
                    exerciseData.score > 70
                      ? "green"
                      : exerciseData.score > 50
                      ? "yellow"
                      : "red",
                }}
              />
              <div className="text-wrapper-2">{exerciseData.score}</div>
              <div className="text-wrapper-3">점</div>
            </div>
          </div>

          {/* Navigation section - ensure CSS classes match for styling */}
          <div className="analysis-navigation">
            {" "}
            {/* This class might need to match structure from other navs if CSS is shared */}
            <div
              className="home"
              onClick={() => navigateTo("main")}
              style={{ cursor: "pointer" }}
            >
              <img className="vector" alt="Home" src={vectorWrapper} />
              <div className="text-wrapper-4">Home</div>
            </div>
            <div className="overlap-2">
              <div
                className="chat"
                onClick={() => navigateTo("chat")}
                style={{ cursor: "pointer" }}
              >
                <div className="rectangle" />
                <img className="img" alt="Chat Bot" src={vector4} />
                <div className="text-wrapper-5">Chat Bot</div>
              </div>
              <div
                className="anlaysis"
                onClick={() => navigateTo("analysis")}
                style={{ cursor: "pointer" }}
              >
                <img className="vector-2" alt="Analysis" src={vector5} />
                <div className="text-wrapper-6">Analysis</div>
              </div>
            </div>
          </div>

          <div className="analysis-times">
            <div className="div-wrapper">
              <div className="text-wrapper-7">
                이번 운동으로 {exerciseData.count}회 했어요!
              </div>
            </div>
          </div>

          <p className="p">{exerciseData.feedback}</p>

          {/* 평가기준 버튼 영역 */}
          <div
            className="evaluation-button-area"
            onClick={toggleEvaluationModal}
            style={{
              cursor: "pointer",
              textAlign: "center",
              marginTop: "20px",
            }}
          >
            <img
              className="evaluation-icon"
              alt="Evaluation Icon"
              src={analysisEvaluationButton}
              style={{ width: "50px", height: "auto" }}
            />
            <div
              className="text-wrapper-8"
              style={{ color: "#4caf50", fontWeight: "bold" }}
            >
              평가기준
            </div>
          </div>

          {/* 평가 기준 모달 */}
          {showEvaluationModal && (
            <div
              className="evaluation-modal-overlay"
              onClick={toggleEvaluationModal}
            >
              {/* 모달 컨텐츠 클릭 시 이벤트 버블링 방지하여 모달이 닫히지 않도록 함 */}
              <div
                className="evaluation-modal-content"
                onClick={(e) => e.stopPropagation()}
              >
                <button
                  className="close-modal-button"
                  onClick={toggleEvaluationModal}
                >
                  &times;
                </button>
                <h2>운동 평가 기준</h2>
                <img
                  className="evaluation-modal-image"
                  alt="Evaluation Criteria"
                  src={
                    analysisEvaluationButton
                  } /* 상세 평가 기준 이미지 또는 내용 */
                />
                {/* 여기에 추가적인 평가 기준 텍스트나 내용을 넣을 수 있습니다. */}
                <p>
                  - 정확한 자세로 수행했는지
                  <br />
                  - 운동 범위가 적절했는지
                  <br />
                  - 설정된 시간/횟수를 잘 따랐는지
                  <br />
                  등을 종합적으로 평가합니다.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
