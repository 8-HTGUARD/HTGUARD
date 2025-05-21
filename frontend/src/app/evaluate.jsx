import React, { useState } from "react";

import "./styles/evaluation.css";
// 이미지 import 추가 (경로는 실제 파일 위치에 맞게 수정해주세요)
import rectangle from "./styles/asset/Rectangle.png"; // 예시 경로

export const Component = () => {
	const [isVisible, setIsVisible] = useState(true);

	const handleClose = () => {
		setIsVisible(false);
	};

	if (!isVisible) {
		return null; // 컴포넌트가 보이지 않도록 null을 반환
	}

	return (
		<div
			className="component"
			onClick={handleClose}
			style={{ cursor: "pointer" }}
		>
			<div className="group">
				<div className="overlap-group">
					<div className="text-wrapper">평가기준</div>
					<img className="rectangle" alt="Rectangle" src={rectangle} />
				</div>
			</div>

			<div className="overlap">
				<p className="div">
					몸짓의 각도를 비교하여 올바른 동작과
					<br />
					비교합니다. (수정 예정)
				</p>
			</div>
		</div>
	);
};
