# Project M.A.R.S. (Multi-source Augmented RAG System)

Project M.A.R.S. is an intelligent chatbot application that leverages Retrieval-Augmented Generation (RAG) to provide answers based on specific web content provided by the user. Unlike general-purpose LLMs, M.A.R.S. can be "taught" new information from a URL, making it a powerful tool for domain-specific queries.

## How it is better than current LLMs

General-purpose Large Language Models (LLMs) have a vast but static knowledge base. Their information is limited to what they were trained on, and they can sometimes provide outdated or incorrect information (a phenomenon known as "hallucination").

M.A.R.S. overcomes these limitations by implementing a RAG pipeline. Here’s how it’s better:

*   **Context-Specific Knowledge:** It can answer questions based on the content of a specific URL you provide. This is ideal for tasks like summarizing articles, querying documentation, or getting information from a very specific knowledge base.
*   **Reduces Hallucination:** By grounding its answers in the provided text, the model is much less likely to make things up.
*   **Up-to-Date Information:** You can feed it a URL with the latest information, and it will be able to answer questions about it, something a general LLM can't do without being retrained.

## How it is Useful

M.A.R.S. can be used in various scenarios:

*   **Research Assistant:** Quickly get answers from a specific research paper or article.
*   **Customer Support:** A support bot that can answer questions based on the company's FAQ page or documentation.
*   **Personalized Learning:** Learn about a new topic by feeding it relevant URLs.

## Flow Diagram

Here is the flow of how the application works:

```
+---------------------+      +----------------------+      +---------------------+
|   User Interface    |      |      Node.js/Express |      |    Python Scripts   |
|      (React)        |      |        Backend       |      |      (RAG Core)     |
+---------------------+      +----------------------+      +---------------------+
          |                            |                             |
          | 1. User provides URL       |                             |
          |--------------------------->| 2. Scrape & Embed           |
          |                            |---------------------------->| 3. Scrape URL content
          |                            |                             |    & create embeddings
          |                            |                             |    & store them.
          |                            |                             |
          | 4. User sends a message    |                             |
          |--------------------------->| 5. Query RAG                |
          |                            |---------------------------->| 6. Retrieve relevant
          |                            |                             |    context from stored
          |                            |                             |    embeddings and
          |                            |                             |    generate answer.
          |                            |                             |
          |                            | 7. Return generated answer  |
          |<---------------------------|                             |
          |                            |                             |
          | 8. Display answer to user  |                             |
          |                            |                             |
```

## Key Features

*   **User Authentication:** Secure user login and registration using JWT.
*   **Chat History:** Saves your conversations for future reference.
*   **RAG Pipeline:** The core feature that allows the chatbot to learn from web content.
*   **Responsive UI:** A clean and simple chat interface.

## How to Run the Project

**Frontend:**
```bash
npm install
npm run dev
```

**Backend:**
```bash
cd backend
npm install
node index.js
```