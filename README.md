# Learning Path Assistant

A Streamlit application that helps users find relevant competencies and course recommendations based on their learning interests.

## How The Algorithm Works

1.  It uses the user query to search for related competencies in a vector database.
2.  It then uses those competencies to search for relevant courses by web scraping https://coniverse.com/.
3.  Finally, it uses an LLM (Large Language Model) to decide which of the found courses are most related to the user's original query and recommends them.

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
