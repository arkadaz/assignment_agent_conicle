# Learning Path Assistant

This application is a Learning Path Assistant built with Streamlit, leveraging a vector database (Qdrant) for competency search, Selenium for web scraping course information, and an LLM (GPT-4o via `pydantic-ai`) for generating personalized course recommendations.

## Features

* Search for relevant competencies based on user input.
* Find related courses from Coniverse.com (via web scraping).
* Generate personalized course recommendations using an LLM.
* Modular code structure for better organization.
* Configuration via environment variables.

## Project Structure

The project is organized into several files:

* `ui_streamlit.py`: The main Streamlit application file. Handles the user interface, session state, and orchestrates calls to other modules.
* `vector_db.py`: Contains logic for loading competency data, initializing and setting up the Qdrant vector database, and performing similarity searches.
* `tools.py`: Houses external tools, specifically the web scraping function (`get_all_coniverse_courses`) using Selenium to fetch course titles.
* `agent.py`: Manages the initialization of the LLM agent and the function for generating the final course recommendation message.
* `models.py`: Defines the data structures (dataclasses) used throughout the application, such as `Competency` and `CourseRecommendation`.
* `settings.py`: Centralizes application configuration constants, reading values from environment variables with defined fallbacks.
* `Dockerfile`: Defines the Docker image for the application.
* `docker-compose.yml`: Defines the service to run the Docker container.
* `requirements.txt`: Lists the Python dependencies.

## Setup and Installation

1.  **Clone the repository (if applicable) or save the files:** Ensure all the Python files (`ui_streamlit.py`, `vector_db.py`, `tools.py`, `agent.py`, `models.py`, `settings.py`), `Dockerfile`, `docker-compose.yml`, and `requirements.txt` are in the same directory.
2.  **Create a data directory:** Create a subdirectory named `data` in the same location.
3.  **Add competency data:** Place your `openai_result - competencies.csv` file inside the `data` directory.
4.  **Create `requirements.txt`:** Ensure you have a `requirements.txt` file listing all necessary Python packages (e.g., `streamlit`, `qdrant-client`, `sentence-transformers`, `pydantic-ai`, `selenium`, `pandas`, `webdriver-manager`).
5.  **Install Docker and Docker Compose:** Make sure you have Docker and Docker Compose installed on your system.

## Configuration

The application's settings are managed in `settings.py`. These settings are read from environment variables first, falling back to default values if the environment variables are not set.

When using Docker Compose, you can define these environment variables in a `.env` file in the same directory as your `docker-compose.yml`, or set them directly in the `docker-compose.yml` file (as shown for `OPENAI_API_KEY`).

Example `.env` file:
```env
OPENAI_API_KEY='your-api-key'
TOP_N=5
LLM_MODEL_NAME="gpt-3.5-turbo"