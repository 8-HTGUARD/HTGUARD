import React, { useState } from "react";
import "./App.css";

import { Main } from "./app/main";
import { Chat } from "./app/chat";
import { Analysis } from "./app/analysis";

function App() {
  // 현재 화면 상태
  const [currentView, setCurrentView] = useState("main");

  // 분석 영상 경로 상태
  const [videoPath, setVideoPath] = useState("");

  // navigateTo 함수 수정: videoPath도 함께 받을 수 있도록
  const navigateTo = (view, data = {}) => {
    setCurrentView(view);
    if (data.videoPath) {
      setVideoPath(data.videoPath);
    }
  };

  return (
    <div className="container">
      <h1>AI 홈트 모니터링</h1>

      <nav className="navigation-tabs">
        <button
          onClick={() => navigateTo("main")}
          className={`nav-button ${currentView === "main" ? "active" : ""}`}
        >
          홈
        </button>
        <button
          onClick={() => navigateTo("chat")}
          className={`nav-button ${currentView === "chat" ? "active" : ""}`}
        >
          챗봇
        </button>
        <button
          onClick={() => navigateTo("analysis")}
          className={`nav-button ${currentView === "analysis" ? "active" : ""}`}
        >
          분석
        </button>
      </nav>

      <main className="view-content">
        {currentView === "main" && <Main navigateTo={navigateTo} />}
        {currentView === "chat" && <Chat navigateTo={navigateTo} />}
        {currentView === "analysis" && (
          <Analysis navigateTo={navigateTo} videoPath={videoPath} />
        )}
      </main>
    </div>
  );
}

export default App;
