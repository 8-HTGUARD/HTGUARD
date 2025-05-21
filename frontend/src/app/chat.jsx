import React, { useState, useEffect, useRef } from "react";

import "./styles/chat.css";

// Images used by CSS background-image (imported but not directly in <img> src in this component)
// These are implicitly used when an element with the corresponding class is rendered.
import logo from "./styles/asset/logo.svg"; // For .logo
import time from "./styles/asset/time.svg"; // For .chat-time background
// wifi, cellular, battery are imported but not directly used by .chat-time CSS as written
// (only the last background-image in a CSS rule applies unless using multiple backgrounds)
import wifi from "./styles/asset/wifi.svg";
import cellular from "./styles/asset/cellular.svg";
import battery from "./styles/asset/battery.svg";
import chatInputIcon from "./styles/asset/chat_input_icon.svg"; // For .input-button background
// Unused imports, likely for a removed bottom navigation:
// import vectorWrapper from "./styles/asset/vector-wrapper.svg";
// import vector4 from "./styles/asset/Vector-4.svg";
// import vector5 from "./styles/asset/Vector-5.svg";

export const Chat = ({ navigateTo = () => {} }) => {
	const [messages, setMessages] = useState([
		{ id: 1, text: "안녕하세요! 무엇을 도와드릴까요?", sender: "bot" },
		{ id: 2, text: "안녕하세요, 질문이 있습니다.", sender: "user" },
	]);
	const [inputValue, setInputValue] = useState("");
	const chatBodyRef = useRef(null);

	useEffect(() => {
		if (chatBodyRef.current) {
			chatBodyRef.current.scrollTop = chatBodyRef.current.scrollHeight;
		}
	}, [messages]);

	const handleSendMessage = () => {
		if (inputValue.trim() === "") return;
		const newMessage = {
			id: Date.now(),
			text: inputValue,
			sender: "user",
		};
		setMessages((prevMessages) => [...prevMessages, newMessage]);
		setInputValue("");
		// TODO: Chatbot API call
	};

	const handleKeyPress = (event) => {
		if (event.key === "Enter" && !event.shiftKey) {
			event.preventDefault();
			handleSendMessage();
		}
	};

	return (
		<div className="chat">
			{/* Logo: Positioned absolutely by CSS (.chat .logo) */}
			<div className="logo"></div>

			<div className="chat-header">
				{/* Chat Time: Styled by CSS (.chat .chat-time), uses time.svg as background */}
				<div className="chat-time">
					{/* wifi, cellular, battery icons would need separate elements or advanced CSS for .chat-time if they are all to be visible */}
				</div>
				<div className="chat-header-name">
					{/* Title: Positioned by CSS (.chat .title) */}
					<div className="title">AI챗봇</div>
				</div>
			</div>

			<div className="chat-body" ref={chatBodyRef}>
				<div className="main">
					{/* Message list container: Styled by CSS (.chat .div) */}
					<div className="div">
						{messages.map((msg) => (
							<div
								key={msg.id}
								className={`message-row ${
									// Base class for spacing
									msg.sender === "bot" ? "bot-message" : "user-message"
								}`} // bot-message/user-message for alignment (needs CSS)
							>
								{msg.sender === "bot" ? (
									<>
										<div className="chat-man-img">
											{" "}
											{/* Bot avatar container */}
											<div className="img">
												<div className="frame" />{" "}
												{/* Bot avatar placeholder/image */}
											</div>
										</div>
										<div className="div2">
											{" "}
											{/* Bot message bubble */}
											<div className="chat-help-mention">
												{" "}
												{/* Text container in bubble */}
												<div className="div3">{msg.text}</div> {/* Bot text */}
											</div>
										</div>
									</>
								) : (
									<>
										<div className="div7">
											{" "}
											{/* User message bubble */}
											<div className="p">
												{" "}
												{/* Text container in bubble */}
												<div className="div8">{msg.text}</div> {/* User text */}
											</div>
										</div>
										<div className="div6">
											{" "}
											{/* User avatar container */}
											<div className="img2">
												<div className="frame2" />{" "}
												{/* User avatar placeholder/image */}
											</div>
										</div>
									</>
								)}
							</div>
						))}
					</div>
				</div>
			</div>

			{/* Chat Input: Positioned absolutely by CSS (.chat .chat-input) */}
			<div className="chat-input">
				{/* Input elements container: Styled by CSS (.chat .div9) */}
				<div className="div9">
					{" "}
					{/* Empty div removed */}
					<div className="chat-input-textbox">
						{/* Input field: Placeholder styled by CSS (.chat .div10 for placeholder text style) */}
						{/* The actual input element will take styles from .chat-input-textbox and its own type styles */}
						<input
							type="text"
							placeholder="메시지를 입력하세요..." // Placeholder text
							value={inputValue}
							onChange={(e) => setInputValue(e.target.value)}
							onKeyPress={handleKeyPress}
							// className="div10" // .div10 styles placeholder text, not the input field itself directly usually
						/>
					</div>
					{/* Send Button: Styled by CSS (.chat .input-button), uses chat_input_icon.svg as background */}
					{/* Consider using a <button> element for better accessibility */}
					<div
						className="input-button"
						onClick={handleSendMessage}
						role="button" // Accessibility: Indicate this div acts as a button
						tabIndex="0" // Accessibility: Make it focusable
						onKeyPress={(e) => e.key === "Enter" && handleSendMessage()} // Accessibility: Allow Enter key press
					></div>
				</div>
			</div>
		</div>
	);
};
