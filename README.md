# Project M.A.R.S. (Multi-source Augmented RAG System)

Project M.A.R.S. is an intelligent chatbot application that leverages Retrieval-Augmented Generation (RAG) to provide answers based on dynamically retrieved web content. It goes a step further by comparing the RAG-generated answer with a response from a standard Large Language Model (LLM) and provides a comprehensive evaluation of both.

## How it is better than current LLMs

General-purpose Large Language Models (LLMs) have a vast but static knowledge base. Their information is limited to what they were trained on, and they can sometimes provide outdated or incorrect information (a phenomenon known as "hallucination").

M.A.R.S. overcomes these limitations by implementing a sophisticated RAG (Retrieval-Augmented Generation) pipeline and a comprehensive evaluation system:

1.  **Dynamic Information Retrieval (RAG Core):**
    *   When a user submits a query, M.A.R.S. first uses a search tool (Serper API) to find relevant web pages.
    *   These web pages are then scraped for their content, and the extracted text is converted into numerical representations (embeddings).
    *   These embeddings are stored in a vector database (Pinecone), creating a dynamic, up-to-date knowledge base specific to the query.
    *   A powerful LLM (Groq's Llama 3.3) then generates an answer, but critically, it is "augmented" with the retrieved and embedded context from the web. This ensures the answer is grounded in current, external information.

2.  **Direct LLM Response:**
    *   Simultaneously, the same LLM generates an answer to the user's query *without* any external context (i.e., a pure LLM response).

3.  **Comprehensive Evaluation:**
    *   Both the RAG-augmented answer and the pure LLM answer are then subjected to a rigorous, multi-metric evaluation process:
        *   **Semantic Similarity:** Measures how semantically similar the two answers are to each other using Sentence-Transformers.
        *   **BERTScore:** Evaluates the quality of the RAG answer against the LLM answer (or vice-versa) by comparing their contextual embeddings, providing precision, recall, and F1 scores.
        *   **Factual Accuracy (QA-based):** A Question-Answering (QA) model (e.g., RoBERTa-base-squad2) is used to assess if key facts from the original query are present and correctly addressed in each answer.
        *   **Judge Model Comparison:** A powerful LLM acts as an impartial judge, comparing both answers qualitatively, providing a justification, and declaring a "winner" based on overall quality, relevance, and completeness.

This multi-faceted approach ensures that M.A.R.S. not only provides context-specific, up-to-date, and less hallucinatory answers but also offers transparency into the performance differences between RAG and pure LLM approaches.

## Flow Diagram

Here is the detailed flow of how the application works:

```
+---------------------+      +----------------------+      +-----------------------------------------------------+
|   User Interface    |      |      Node.js/Express |      |    Python Scripts (RAG Core & Evaluation)           |
|      (React)        |      |        Backend       |      |                                                     |
+---------------------+      +----------------------+      +-----------------------------------------------------+
          |                            |                                               |
          | 1. User submits query      |                                               |
          |    (always triggers        |                                               |
          |    comparison)             |                                               |
          |--------------------------->| 2. Backend receives query                     |
          |                            |    and invokes `rag_query_compare.py`         |
          |                            |---------------------------------------------->| 3. `rag_query_compare.py` starts:
          |                            |                                               |    a. **Dynamic Data Ingestion:**
          |                            |                                               |       - Uses `searchurl.py` (Serper API) to find relevant URLs.
          |                            |                                               |       - Uses `webscrap.py` to scrape content from found URLs.
          |                            |                                               |       - Embeds scraped content using `SentenceTransformer`.
          |                            |                                               |       - Upserts embeddings to Pinecone vector database.
          |                            |                                               |    b. **RAG Answer Generation:**
          |                            |                                               |       - Retrieves most relevant documents from Pinecone based on query.
          |                            |                                               |       - Constructs a prompt with retrieved context.
          |                            |                                               |       - Sends prompt to Groq LLM (`llama-3.3-70b-versatile`) for RAG answer.
          |                            |                                               |    c. **Pure LLM Answer Generation:**
          |                            |                                               |       - Sends original query directly to Groq LLM (`llama-3.3-70b-versatile`) for a non-RAG answer.
          |                            |                                               |    d. **Comprehensive Evaluation:**
          |                            |                                               |       - Calls `comprehensive_evaluate.py` with query, RAG answer, and LLM answer.
          |                            |                                               |       - `comprehensive_evaluate.py` calculates:
          |                            |                                               |         - Semantic Similarity (Sentence-Transformers)
          |                            |                                               |         - BERTScore (between RAG and LLM answers)
          |                            |                                               |         - Factual Accuracy (QA model, e.g., RoBERTa-base-squad2)
          |                            |                                               |         - Judge Model Evaluation (Groq LLM for qualitative comparison & winner)
          |                            |                                               |       - Returns all evaluation scores and winner.
          |                            |                                               |
          |<---------------------------| 4. `rag_query_compare.py` returns a single    |
          |                            |    JSON object containing RAG answer, LLM     |
          |                            |    answer, and comprehensive evaluation.      |
          |                            |                                               |
          | 5. Backend sends this      |                                               |
          |    data to the frontend    |                                               |
          |<---------------------------|                                               |
          | 6. Frontend displays       |                                               |
          |    side-by-side comparison |                                               |
          |    of answers, detailed    |                                               |
          |    evaluation metrics,     |                                               |
          |    and a visual graph.     |                                               |
          |                            |                                               |
```

## Key Features

*   **User Authentication:** Secure user login and registration using JWT.
*   **Chat History:** Saves your conversations for future reference.
*   **RAG vs. LLM Comparison:** The core feature that provides a side-by-side comparison of answers from a RAG model and a standard LLM.
*   **Comprehensive Evaluation:** A sophisticated evaluation pipeline that uses multiple metrics to assess the quality of the generated answers.
*   **Visual Comparison:** A graph to visually compare the performance of the two models.
*   **Responsive UI:** A clean and simple chat interface.

## Technologies Used

*   **Frontend:** React, Vite, Axios, Recharts
*   **Backend:** Node.js, Express, Mongoose, JWT
*   **Python:** Sentence-transformers, Pinecone, Groq, BERT-Score, Transformers

## Project Structure

```
.
├── backend
│   ├── db.js
│   ├── docker.yaml
│   ├── index.js
│   ├── middleware
│   │   └── fetchuser.js
│   ├── models
│   │   ├── Chat.js
│   │   ├── Score.js
│   │   └── User.js
│   ├── node
│   │   ├── comprehensive_evaluate.py
│   │   ├── embed_and_upload.py
│   │   ├── rag_query.py
│   │   ├── rag_query_compare.py
│   │   ├── reward_memory.json
│   │   ├── scraped_data.json
│   │   ├── searchurl.py
│   │   └── webscrap.py
│   ├── package.json
│   └── routes
│       ├── auth.js
│       ├── chat.js
│       └── rag.js
├── public
│   └── vite.svg
├── src
│   ├── assets
│   │   └── react.svg
│   ├── components
│   │   ├── ChatArea.jsx
│   │   ├── ComparisonGraph.jsx
│   │   ├── ComparisonMessage.jsx
│   │   ├── EvaluationDetails.jsx
│   │   ├── Header.jsx
│   │   ├── Message.jsx
│   │   ├── MessageInput.jsx
│   │   ├── Shimmer.jsx
│   │   └── Sidebar.jsx
│   ├── pages
│   │   ├── ChatDetailsPage.jsx
│   │   ├── ChatHistoryPage.jsx
│   │   ├── LoginPage.jsx
│   │   └── SignupPage.jsx
│   ├── App.css
│   ├── App.jsx
│   ├── index.css
│   └── main.jsx
├── .gitignore
├── eslint.config.js
├── index.html
├── package.json
├── README.md
└── vite.config.js
```

## API Endpoints

*   `POST /api/auth/signup`: Create a new user.
*   `POST /api/auth/login`: Login a user.
*   `GET /api/auth/getuser`: Get the logged-in user's data.
*   `POST /api/chat/save`: Save a chat conversation.
*   `GET /api/chat/history`: Get the chat history for the logged-in user.
*   `GET /api/chat/:id`: Get a specific chat conversation.
*   `DELETE /api/chat/:id`: Delete a specific chat conversation.
*   `POST /api/rag/query`: Get a response from the RAG model (not used in the current UI).
*   `POST /api/rag/compare`: Get a comparison between the RAG and LLM models.

## Python Scripts

*   `rag_query_compare.py`: The main script that orchestrates the comparison pipeline. It takes a user query, generates RAG and LLM answers, and calls the evaluation script.
*   `comprehensive_evaluate.py`: Performs a comprehensive evaluation of the two answers using various metrics.
*   `rag_query.py`: A script for querying the RAG model (not used in the current comparison pipeline).
*   `embed_and_upload.py`: A utility script to embed and upload data to the Pinecone vector database.
*   `searchurl.py`: A utility script to search for URLs based on a query using the Serper API.
*   `webscrap.py`: A utility script to scrape the content of a webpage.

## How to Run the Project

### Prerequisites

*   Node.js
*   Python 3.10+
*   MongoDB

### Backend Setup

1.  **Navigate to the `backend` directory:**
    ```bash
    cd backend
    ```

2.  **Install Node.js dependencies:**
    ```bash
    npm install
    ```

3.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: You may need to create a `requirements.txt` file first. See the "Python Dependencies" section below.)*

4.  **Create a `.env` file** in the `backend` directory and add the following environment variables:
    ```
    MONGO_URI=<your_mongodb_uri>
    JWT_SECRET=<your_jwt_secret>
    PINECONE_API_KEY=<your_pinecone_api_key>
    GROQ_API_KEY=<your_groq_api_key>
    SERPER_API_KEY=<your_serper_api_key>
    ```

5.  **Start the backend server:**
    ```bash
    node index.js
    ```

### Frontend Setup

1.  **Navigate to the root directory.**

2.  **Install Node.js dependencies:**
    ```bash
    npm install
    ```

3.  **Start the frontend development server:**
    ```bash
    npm run dev
    ```

### Python Dependencies

The Python scripts require the following libraries. You can install them using pip:
```bash
pip install sentence-transformers pinecone-client groq bert-score torch transformers beautifulsoup4 requests python-dotenv
```

You can also create a `requirements.txt` file with the following content and run `pip install -r requirements.txt`:
```
sentence-transformers
pinecone-client
groq
bert-score
torch
transformers
beautifulsoup4
requests
python-dotenv
```
