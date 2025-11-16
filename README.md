# Project M.A.R.S. (Multi-source Augmented RAG System)

Project M.A.R.S. is an intelligent chatbot application that leverages Retrieval-Augmented Generation (RAG) to provide answers based on dynamically retrieved web content. It goes a step further by comparing the RAG-generated answer with a response from a standard Large Language Model (LLM) and provides a comprehensive evaluation of both.

## How it is better than current LLMs

General-purpose Large Language Models (LLMs) have a vast but static knowledge base. Their information is limited to what they were trained on, and they can sometimes provide outdated or incorrect information (a phenomenon known as "hallucination").

M.A.R.S. overcomes these limitations by:

*   **Context-Specific Knowledge:** It can answer questions based on the content of relevant URLs retrieved based on the user's query.
*   **Reduces Hallucination:** By grounding its answers in the provided text, the RAG model is much less likely to make things up.
*   **Up-to-Date Information:** It can access the latest information available on the web.
*   **Comprehensive Evaluation:** It provides a detailed comparison between the RAG and standard LLM answers, using a variety of metrics, to help the user understand the strengths and weaknesses of each approach.

## Flow Diagram

Here is the flow of how the application works:

```
+---------------------+      +----------------------+      +---------------------+
|   User Interface    |      |      Node.js/Express |      |    Python Scripts   |
|      (React)        |      |        Backend       |      |      (RAG Core)     |
+---------------------+      +----------------------+      +---------------------+
          |                            |                             |
          | 1. User sends query        |                             |
          |--------------------------->| 2. Backend calls Python     |
          |                            |    script for comparison    |
          |                            |--------------------------->| 3. Python script:
          |                            |                             |    - Scrapes web for context
          |                            |                             |    - Generates RAG answer
          |                            |                             |    - Generates LLM answer
          |                            |                             |    - Performs comprehensive
          |                            |                             |      evaluation
          |                            |                             |
          |                            | 4. Return RAG answer,       |
          |<---------------------------|    LLM answer, and          |
          |                            |    evaluation to backend    |
          |                            |                             |
          | 5. Backend sends data to   |                             |
          |    frontend                |                             |
          |                            |                             |
          | 6. Display comparison      |                             |
          |    and evaluation to user  |                             |
          |                            |                             |
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
