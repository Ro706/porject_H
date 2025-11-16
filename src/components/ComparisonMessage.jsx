import React, { useState } from 'react';
import { motion } from 'framer-motion';
import './ComparisonMessage.css';

const ComparisonMessage = ({ message }) => {
    const { rag_answer, llm_answer, query_id } = message;
    const [ragVote, setRagVote] = useState(null);
    const [llmVote, setLlmVote] = useState(null);

    const handleVote = async (model, vote) => {
        if (model === 'rag') {
            setRagVote(vote);
            setLlmVote(null); 
        } else {
            setLlmVote(vote);
            setRagVote(null);
        }

        try {
            const token = localStorage.getItem('token');
            await fetch('http://localhost:5800/api/chat/rate', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'auth-token': token
                },
                body: JSON.stringify({ query_id, model, vote }),
            });
        } catch (error) {
            console.error('Failed to submit vote:', error);
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="comparison-message-container"
        >
            <div className="comparison-responses">
                <div className="comparison-response-item">
                    <h3>RAG Model</h3>
                    <div className="comparison-message-text">{rag_answer}</div>
                    <div className="comparison-voting">
                        <button
                            onClick={() => handleVote('rag', 'up')}
                            className={ragVote === 'up' ? 'selected' : ''}
                        >
                            👍
                        </button>
                        <button
                            onClick={() => handleVote('rag', 'down')}
                            className={ragVote === 'down' ? 'selected' : ''}
                        >
                            👎
                        </button>
                    </div>
                </div>
                <div className="comparison-response-item">
                    <h3>LLM</h3>
                    <div className="comparison-message-text">{llm_answer}</div>
                    <div className="comparison-voting">
                        <button
                            onClick={() => handleVote('llm', 'up')}
                            className={llmVote === 'up' ? 'selected' : ''}
                        >
                            👍
                        </button>
                        <button
                            onClick={() => handleVote('llm', 'down')}
                            className={llmVote === 'down' ? 'selected' : ''}
                        >
                            👎
                        </button>
                    </div>
                </div>
            </div>
        </motion.div>
    );
};

export default ComparisonMessage;
