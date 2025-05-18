# Learning Path Assistant

This application is a Learning Path Assistant built with Streamlit, leveraging a vector database (Qdrant) for competency search, Selenium for web scraping course information, and an LLM (GPT-4o via `pydantic-ai`) for generating personalized course recommendations.

It helps users discover relevant competencies based on their input and finds potentially related courses from Coniverse.com, using an AI model to filter and recommend the most suitable ones.

## Features

* Search for relevant competencies based on user input using a vector database.
* Find related courses from Coniverse.com by web scraping search results.
* Generate personalized course recommendations using an LLM, filtering irrelevant courses.
* Modular code structure for better organization and maintainability.
* Configuration managed through environment variables for flexibility.

## Project Structure

The project is organized into the following files and directories:

* `ui_streamlit.py`: The main Streamlit application file. It handles the user interface, manages session state, and orchestrates calls to other modules for searching competencies, scraping courses, and generating recommendations.
* `vector_db.py`: Contains the logic for handling competency data. This includes loading data from the CSV, initializing and setting up the Qdrant vector database, embedding competencies, and performing similarity searches based on user queries.
* `tools.py`: Houses external tools used by the application. Currently, this includes the web scraping function (`get_all_coniverse_courses`) which uses Selenium to fetch potential course titles from Coniverse.com.
* `agent.py`: Manages the initialization and interaction with the Large Language Model (LLM). It contains the function responsible for generating the final course recommendation message by filtering and processing the scraped course data using the LLM.
* `models.py`: Defines the data structures (using Python's `dataclasses`) used throughout the application. Examples include `Competency` to structure competency data and `CourseRecommendation` for the LLM's output format.
* `settings.py`: Centralizes the application's configuration. It reads settings such as API keys, database parameters, and model names from environment variables, providing default values if variables are not set.
* `Dockerfile`: Defines the Docker image for the application, specifying the base image, dependencies, and entry point.
* `docker-compose.yml`: Defines the service to run the Docker container, including port mappings and environment variable configuration.
* `requirements.txt`: Lists all the Python dependencies required to run the application.

## Setup and Installation

To set up and run this project, follow these steps:

1.  **Clone the repository (if applicable) or save the files:** Ensure all the Python files (`ui_streamlit.py`, `vector_db.py`, `tools.py`, `agent.py`, `models.py`, `settings.py`), `Dockerfile`, `docker-compose.yml`, and `requirements.txt` are in the same directory.
2.  **Create a data directory:** Create a subdirectory named `data` in the same location as the project files.
3.  **Add competency data:** Place your competency data file, named `openai_result - competencies.csv`, inside the newly created `data` directory.
4.  **Create `requirements.txt`:** Ensure you have a `requirements.txt` file in the project root listing all necessary Python packages. A typical list would include:
    ```
    streamlit
    qdrant-client
    sentence-transformers
    pydantic-ai
    selenium
    pandas
    webdriver-manager
    python-dotenv # Useful for loading .env files with docker-compose
    ```
5.  **Install Docker and Docker Compose:** Make sure you have Docker and Docker Compose installed on your system. You can find installation instructions on the [official Docker website](https://docs.docker.com/get-docker/).

## Configuration

The application's behavior is controlled by settings defined in `settings.py`. These settings primarily read values from environment variables.

When using Docker Compose, the easiest way to manage environment variables is by creating a `.env` file in the same directory as your `docker-compose.yml`. Docker Compose will automatically load variables from this file. Alternatively, you can define them directly in the `docker-compose.yml` file under the `environment` section for the service.

Example `.env` file:

```env
# Required: Your OpenAI API key for the LLM
OPENAI_API_KEY='your-api-key'

# Optional: Number of top competencies to retrieve from the vector DB (default is 5)
TOP_N=5

# Optional: Name of the LLM model to use (default is "gpt-4o" if not specified in code/settings)
LLM_MODEL_NAME="gpt-4o"

# Optional: URL for the Qdrant database if running externally (default is in-memory)
# QDRANT_URL="http://localhost:6333"

# Optional: API Key for Qdrant if required
# QDRANT_API_KEY="your-qdrant-api-key"