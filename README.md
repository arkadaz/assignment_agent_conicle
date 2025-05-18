# Learning Path Assistant

A Streamlit application that helps users find relevant competencies and course recommendations based on their learning interests.

## How The Algorithm Works

1.  **Vector Database Search**:
    * User queries are converted to vector embeddings using sentence-transformers
    * These embeddings are compared against stored competency embeddings in Qdrant
    * The most semantically similar competencies are retrieved

2.  **Web Scraping for Courses**:
    * Selected competencies are used as search terms on Coniverse.com
    * Selenium automates the browser to collect course titles and details
    * Results are aggregated across all selected competencies

3.  **LLM-Based Recommendation**:
    * GPT-4o processes raw course data along with user context
    * The model filters out irrelevant courses and ranks the most suitable ones
    * Personalized recommendations are presented with explanations

## Running The Application

### Prerequisites

* Docker and Docker Compose installed
* Competency CSV file (`openai_result - competencies.csv`) in a `data` directory
* OpenAI API key

### Steps to Run

1.  Export your OpenAI API key in your terminal **before** running the docker compose command:
    ```bash
    export OPENAI_API_KEY='your-openai-api-key'
    ```
    Replace `your-openai-api-key` with your actual OpenAI API key. *Note: This variable will only be set for your current terminal session. You will need to run this command again if you open a new terminal.*

2.  Build and start with Docker Compose:
    ```bash
    docker-compose up --build
    ```

3.  Access the application at:
    ```
    http://localhost:8080
    ```