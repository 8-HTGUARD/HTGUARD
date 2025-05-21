import React, { useState, useRef } from "react";
import "./styles/main.css"; // Your main.css file

// Import images. While CSS handles background-images,
// importing them here can be useful for webpack/bundler processing or if you decide to use them in <img> tags.
// For <img> tags, you definitely need to import the image.

// Assets used by CSS background-image (CSS loader will handle these paths)
import logoAsset from "./styles/asset/logo.svg";
import timeAsset from "./styles/asset/time.svg";
import batteryAsset from "./styles/asset/battery.svg";
import cellularAsset from "./styles/asset/cellular.svg";
import wifiAsset from "./styles/asset/wifi.svg";
import cameraButtonIconAsset from "./styles/asset/camera.svg"; // For .vector-2
import uploadButtonIconAsset from "./styles/asset/upload.svg"; // For .vector-3
import chatbotNavIconAsset from "./styles/asset/Vector-4.svg"; // For .vector-4
import analysisNavIconAsset from "./styles/asset/Vector-5.svg"; // For .vector-5
import homeNavIconBgAsset from "./styles/asset/vector-wrapper.svg"; // For .vector-wrapper

// Icon for <img> tag (e.g., calendar icon)
import calendarIcon from "./styles/asset/camera.svg"; // Assuming camera.svg can be used, or replace with actual calendar.svg

export const Main = ({ navigateTo = () => {} }) => {
	const [selectedCategory, setSelectedCategory] = useState(null);
	const [selectedVideo, setSelectedVideo] = useState(null);
	const [videoThumbnail, setVideoThumbnail] = useState(null);
	const [isVideoUploaded, setIsVideoUploaded] = useState(false);
	const fileInputRef = useRef(null);

	const handleNavigate = (path) => {
		navigateTo(path);
	};

	const handleCategorySelect = (category) => {
		setSelectedCategory(category);
		console.log(`${category} 선택됨`);
	};

	const triggerVideoUpload = () => {
		if (fileInputRef.current) {
			fileInputRef.current.click();
		}
	};

	const handleVideoFileChange = (event) => {
		const file = event.target.files[0];
		if (file && file.type.startsWith("video/")) {
			setSelectedVideo(file);
			const thumbnailUrl = URL.createObjectURL(file);
			setVideoThumbnail(thumbnailUrl);
			setIsVideoUploaded(true);
			console.log("비디오 선택됨:", file.name);
		} else {
			alert("비디오 파일을 선택해주세요.");
			setSelectedVideo(null);
			setVideoThumbnail(null);
			setIsVideoUploaded(false);
		}
	};

	const handleAnalyzeClick = () => {
		if (!selectedVideo) {
			alert("분석할 비디오를 먼저 업로드해주세요.");
			return;
		}
		if (!selectedCategory) {
			alert("운동 카테고리를 선택해주세요.");
			return;
		}
		console.log(
			`분석 페이지로 이동: 비디오 - ${selectedVideo.name}, 카테고리 - ${selectedCategory}`
		);
		navigateTo("analysis"); // Pass data as needed: navigateTo("analysis", { video: selectedVideo, category: selectedCategory });
	};

	return (
		<div className="main">
			<div className="header">
				<div className="logo"></div>{" "}
				{/* Styled by .main .logo with background-image */}
				<div className="overlap-group">
					{" "}
					{/* Container for status bar icons */}
					<div className="top">
						{" "}
						{/* Base for status bar */}
						<div className="time"></div> {/* Styled by .main .time */}
						<div className="battery"></div> {/* Styled by .main .battery */}
						<div className="cellular"></div>
						{/* Styled by .main .cellular */}
						<div className="wifi"></div> {/* Styled by .main .wifi */}
					</div>
				</div>
			</div>

			<div className="category">
				<div className="text-wrapper">운동 자세 선택</div>
				<div className="chip-group">
					{["플랭크", "런지", "푸쉬업"].map((cat) => (
						<div
							key={cat}
							className={`chip ${selectedCategory === cat ? "selected" : ""}`} // Add "selected" class for styling active chip
							onClick={() => handleCategorySelect(cat)}
						>
							<div className="element">{cat}</div>
						</div>
					))}
				</div>
				<div className="info">
					{selectedCategory
						? `선택된 운동: ${selectedCategory}`
						: "운동 카테고리를 선택하세요."}
				</div>
			</div>

			<div className="view">
				{" "}
				{/* Main content/guide/thumbnail area */}
				{/* .section-title, .title, .div, .vector, .img are styled by CSS */}
				{/* You can integrate your guide/thumbnail logic here */}
				{!isVideoUploaded ? (
					<div className="guide-text-container">
						{" "}
						{/* Custom container for guide text */}
						<div className="section-title">
							<div className="text">
								<div className="title">운동 가이드</div>
							</div>
						</div>
						<div className="div">
							{" "}
							{/* .main .div for text content */}
							{selectedCategory
								? `${selectedCategory} 운동 가이드가 여기에 표시됩니다.`
								: "운동을 선택하면 가이드가 표시됩니다."}
						</div>
					</div>
				) : (
					videoThumbnail && (
						<div
							className="thumbnail-display"
							style={{ width: "100%", height: "100%" }}
						>
							<video
								src={videoThumbnail}
								alt="Video thumbnail"
								style={{ width: "100%", height: "100%", objectFit: "cover" }}
								controls={false}
								onLoadedData={() => URL.revokeObjectURL(videoThumbnail)}
							/>
						</div>
					)
				)}
				{/* <div className="img"></div> */} {/* Separator line, if needed */}
				{/* <div className="vector"></div> */}{" "}
				{/* Another separator line, if needed */}
			</div>

			<div className="view-2">
				{" "}
				{/* Buttons container */}
				<div
					className="camera"
					onClick={() => {
						if (!selectedCategory) {
							alert("운동 카테고리를 선택해주세요.");
							return;
						}
						alert("실시간 분석 기능은 준비 중입니다.");
					}}
				>
					<div className="text-wrapper-2">실시간 분석</div>
					<div className="vector-2"></div>{" "}
					{/* Camera icon via CSS .main .vector-2 */}
				</div>
				{!isVideoUploaded ? (
					<div className="upload" onClick={triggerVideoUpload}>
						<div className="upload-2">업로드</div>
						<div className="material-symbols">
							{" "}
							{/* Icon container */}
							<div className="vector-3"></div>{" "}
							{/* Upload icon via CSS .main .vector-3 */}
						</div>
					</div>
				) : (
					<div
						className="analyze-actions-container"
						style={{
							display: "flex",
							gap: "10px",
							justifyContent: "center",
							width: "100%",
						}}
					>
						<button
							className="custom-button analyze-button"
							onClick={handleAnalyzeClick}
						>
							분석하기
						</button>
						<button
							className="custom-button re-upload-button"
							onClick={() => {
								setIsVideoUploaded(false);
								setSelectedVideo(null);
								if (videoThumbnail) URL.revokeObjectURL(videoThumbnail);
								setVideoThumbnail(null);
								if (fileInputRef.current) fileInputRef.current.value = "";
								triggerVideoUpload();
							}}
						>
							다른 영상
						</button>
					</div>
				)}
				<input
					type="file"
					ref={fileInputRef}
					style={{ display: "none" }}
					accept="video/*"
					onChange={handleVideoFileChange}
				/>
			</div>

			<div className="input">
				{" "}
				{/* Date input section */}
				<div
					className="textfield"
					onClick={() => alert("날짜 선택 기능 구현 예정")}
				>
					<div className="text-2">날짜 선택</div>
					{/* Calendar icon using <img> tag */}
					<img
						src={calendarIcon}
						alt="Calendar"
						style={{ width: "20px", height: "20px" }}
					/>
				</div>
			</div>

			{/* This .image section seems like a separate feature display / carousel */}
			<div className="image">
				<div className="p">운동 자세를 위한 가이드</div>
				<div className="pagination">
					<div className="rectangle"></div> {/* Active dot */}
					<div className="rectangle-2"></div>
					<div className="rectangle-2"></div>
				</div>
			</div>
			{/* <div className="text-wrapper-3">Some other text</div> */}
		</div>
	);
};
