import React from 'react';
import EvaluationDetails from './EvaluationDetails';
import ComparisonGraph from './ComparisonGraph';
import './ComparisonMessage.css';

const ComparisonMessage = ({ message }) => {
    const { rag_answer, llm_answer, evaluation } = message;

    return (
        <div className="comparison-message">
            <div className="comparison-answers">
                <div className="answer-column">
                    <h3>RAG Answer</h3>
                    <p>{rag_answer}</p>
                </div>
                <div className="answer-column">
                    <h3>LLM Answer</h3>
                    <p>{llm_answer}</p>
                </div>
            </div>
            {evaluation && (
                <div className="evaluation-section">
                    <EvaluationDetails evaluation={evaluation} />
                    <ComparisonGraph evaluation={evaluation} />
                </div>
            )}
        </div>
    );
};

export default ComparisonMessage;
