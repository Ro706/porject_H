import React, { useState } from 'react';
import { FiSend } from 'react-icons/fi';
import { LuDiff } from 'react-icons/lu';
import './MessageInput.css';

const MessageInput = ({ onSendMessage }) => {
    const [input, setInput] = useState('');

    const handleSend = (compare = false) => {
        if (input.trim()) {
            onSendMessage.current(input, compare);
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
                    <button className="message-input-button send-button" onClick={() => handleSend(false)}>
                        <FiSend />
                    </button>
                    <button className="message-input-button compare-button" onClick={() => handleSend(true)}>
                        <LuDiff />
                    </button>
                </div>
            </div>
        </div>
    );
};

export default MessageInput;