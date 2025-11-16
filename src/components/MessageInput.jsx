import React, { useState } from 'react';
import { FiSend } from 'react-icons/fi';
import './MessageInput.css';

const MessageInput = ({ onSendMessage }) => {
    const [input, setInput] = useState('');

    const handleSend = () => {
        if (input.trim()) {
            onSendMessage.current(input, true); // Always trigger comparison
            setInput('');
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter') {
            handleSend();
        }
    };

    return (
        <div className="message-input-container">
            <div className="message-input-wrapper">
                <input
                    type="text"
                    placeholder="Type your message..."
                    className="message-input"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                />
                <div className="message-input-actions">
                    <button className="message-input-button send-button" onClick={handleSend}>
                        <FiSend />
                    </button>
                </div>
            </div>
        </div>
    );
};

export default MessageInput;