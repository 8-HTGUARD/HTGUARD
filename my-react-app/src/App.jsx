import React, { useState } from "react";
import "./App.css"; // App.css 파일을 사용하도록 주석 해제
// Main 컴포넌트를 가져옵니다. main.jsx 파일의 경로가 src/app/main.jsx라고 가정합니다.
import { Main } from "./app/main";
import { Chat } from "./app/chat";
import Analysis from "./app/analysis"; // Analysis 컴포넌트 사용 시 주석 해제
// import { evaluate } from "./app/evaluate"; // evaluate 컴포넌트는 현재 App.jsx에서 직접 사용되지 않음

function App() {
	// 현재 활성화된 뷰를 관리하는 상태 ('main', 'chat', 'analysis')
	// 기본값으로 'main' (홈 화면)을 설정합니다.
	const [currentView, setCurrentView] = useState("main");

	// 뷰를 변경하는 함수
	const navigateTo = (view) => {
		setCurrentView(view);
	};

	return (
		<div className="container">
			{/* <h1>AI 홈트 모니터링</h1>  // 제목은 각 페이지에서 관리하거나, 필요시 여기에 유지 */}

			{/* 네비게이션 탭 UI */}
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

			{/* 현재 선택된 뷰에 따라 해당 컴포넌트를 렌더링 */}
			<main className="view-content">
				{currentView === "main" && <Main navigateTo={navigateTo} />}
				{currentView === "chat" && <Chat navigateTo={navigateTo} />}
				{currentView === "analysis" && <Analysis navigateTo={navigateTo} />}
			</main>
		</div>
	);
}

export default App;
