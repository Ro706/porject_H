import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import Message from './Message';
import ComparisonMessage from './ComparisonMessage';
import TypingIndicator from './TypingIndicator';
import Shimmer from './Shimmer';
import './ChatArea.css';

const ChatArea = ({ onSendMessage, messages, setMessages }) => {
    const [loading, setLoading] = useState(false);
    const chatEndRef = useRef(null);

    const scrollToBottom = () => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const saveChat = async (currentMessages) => {
        const token = localStorage.getItem('token');
        if (!token || currentMessages.length === 0) return;

        const messagesToSave = currentMessages.map(msg => ({
            ...msg,
            timestamp: msg.timestamp ? new Date(msg.timestamp).toISOString() : new Date().toISOString()
        }));

        try {
            await axios.post('http://localhost:5800/api/chat/save', { messages: messagesToSave }, {
                headers: {
                    'auth-token': token,
                },
            });
            console.log('Chat saved successfully!');
        } catch (error) {
            console.error('Error saving chat:', error);
        }
    };

    const fetchResponse = async (query) => {
        setLoading(true);
        try {
            const token = localStorage.getItem('token');
            const response = await axios.post('http://localhost:5800/api/rag/query', { query }, {
                headers: {
                    'auth-token': token,
                },
            });
            const { answer, reward_score } = response.data;

            const formattedRewardScore = (reward_score * 100).toFixed(2);
            const botMessage = { text: `${answer}\n\nReward Score: ${formattedRewardScore}%`, sender: 'bot', timestamp: new Date().toISOString() };
            setMessages((prevMessages) => [...prevMessages, botMessage]);
        } catch (error) {
            console.error('Error fetching response:', error);
            const errorMessage = { text: 'Sorry, something went wrong.', sender: 'bot', timestamp: new Date().toISOString() };
            setMessages((prevMessages) => [...prevMessages, errorMessage]);
        } finally {
            setLoading(false);
        }
    };

    const fetchComparisonResponse = async (query) => {
        setLoading(true);
        try {
            const token = localStorage.getItem('token');
            const response = await axios.post('http://localhost:5800/api/rag/compare', { query }, {
                headers: {
                    'auth-token': token,
                },
            });
            const { rag_answer, llm_answer } = response.data;

            const comparisonMessage = {
                type: 'comparison',
                rag_answer,
                llm_answer,
                query_id: new Date().getTime(), // Simple unique ID for now
                timestamp: new Date().toISOString()
            };
            setMessages((prevMessages) => [...prevMessages, comparisonMessage]);
        } catch (error) {
            console.error('Error fetching comparison response:', error);
            const errorMessage = { text: 'Sorry, something went wrong with the comparison.', sender: 'bot', timestamp: new Date().toISOString() };
            setMessages((prevMessages) => [...prevMessages, errorMessage]);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (onSendMessage) {
            onSendMessage.current = (query, compare = false) => {
                const newMessage = { text: query, sender: 'user', timestamp: new Date().toISOString() };
                setMessages((prevMessages) => [...prevMessages, newMessage]);
                if (compare) {
                    fetchComparisonResponse(query);
                } else {
                    fetchResponse(query);
                }
            };
        }
    }, [onSendMessage, setMessages]);

    useEffect(() => {
        return () => {
            if (messages.length > 0) {
                saveChat(messages);
            }
        };
    }, [messages]);

    return (
        <div className="chat-area">
            <div className="chat-messages">
                {messages.map((message, index) => {
                    if (message.type === 'comparison') {
                        return <ComparisonMessage key={index} message={message} />;
                    }
                    return <Message key={index} message={message} />;
                })}
                {loading && (
                    <div className="message-container bot">
                        <Shimmer />
                    </div>
                )}
                <div ref={chatEndRef} />
            </div>
        </div>
    );
};

export default ChatArea;