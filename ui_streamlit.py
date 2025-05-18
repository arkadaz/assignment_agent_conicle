import streamlit as st

import settings
from agent import generate_course_message_with_llm, init_llm_agent
from models import Competency
from tools import get_all_coniverse_courses
from vector_db import (
    init_model_and_db,
    load_competency_data,
    search_competencies,
    setup_vector_db,
)

st.set_page_config(page_title="Learning Path Assistant", page_icon="🧠", layout="wide")


if "initialized" not in st.session_state:
    st.session_state.initialized = False
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! I'm your Learning Path Assistant. Tell me about a skill or competency you're interested in developing, and I'll help you discover relevant competencies and suggest courses.",
        }
    ]
if "search_results" not in st.session_state:
    st.session_state.search_results = {}
if "competencies" not in st.session_state:
    st.session_state.competencies = []
if "current_search_index" not in st.session_state:
    st.session_state.current_search_index = -1
if "total_search_count" not in st.session_state:
    st.session_state.total_search_count = 0
if "user_query" not in st.session_state:
    st.session_state.user_query = ""
if "llm_agent" not in st.session_state:
    st.session_state.llm_agent = None
if "final_message_added_for_current_search" not in st.session_state:
    st.session_state.final_message_added_for_current_search = False


def format_competencies_message(competencies: list[Competency]):
    if not competencies:
        return "I couldn't find any relevant competencies based on your input. Could you provide more details or try different keywords?"

    message = "Based on your interest, I've identified these relevant competencies:\n\n"

    for i, comp in enumerate(competencies):
        score_percent = int(comp.similarity_score * 100)
        message += f"**{i + 1}. {comp.name}** ({score_percent}% match)\n"
        message += f"{comp.description}\n\n"

    message += "I'm now searching for courses related to these competencies. This might take a moment..."

    return message


def format_searching_message(competency_name: str, index: int, total: int):
    return f"Searching for courses related to **{competency_name}** ({index + 1}/{total})...."


def process_user_input(user_input: str):
    st.session_state.user_query = user_input

    st.session_state.search_results = {}
    st.session_state.competencies = []
    st.session_state.current_search_index = -1
    st.session_state.total_search_count = 0
    st.session_state.final_message_added_for_current_search = False

    try:
        competencies = search_competencies(
            st.session_state.client,
            st.session_state.model,
            user_input,
            collection_name=settings.QDRANT_COLLECTION_NAME,
            top_n=settings.TOP_N,
            similarity_threshold=settings.SIMILARITY_THRESHOLD,
        )
        st.session_state.competencies = competencies

        if competencies:
            st.session_state.current_search_index = 0
            st.session_state.total_search_count = len(competencies)
            return format_competencies_message(competencies)
        else:
            st.session_state.current_search_index = -1
            st.session_state.total_search_count = 0
            st.session_state.final_message_added_for_current_search = True
            return "I couldn't find any relevant competencies based on your input. Could you provide more details or try different keywords?"
    except Exception as e:
        st.error(f"Error during competency search: {e}")
        st.session_state.current_search_index = -1
        st.session_state.total_search_count = 0
        st.session_state.final_message_added_for_current_search = True
        return "Sorry, an error occurred while searching for competencies."


def main():
    st.title("🧠 Learning Path Assistant")

    with st.sidebar:
        st.subheader("About this Assistant")
        st.write("""
        This Learning Path Assistant helps you discover competencies and suggests relevant courses
        based on your interests. Simply chat with the assistant about skills or areas you want to develop.

        **How it works:**
        1. Enter your interests or skills.
        2. The assistant finds relevant competencies using a vector database.
        3. It searches online for courses related to those competencies (this step might be unreliable due to web scraping).
        4. An AI model (GPT-4o) generates personalized course recommendations based on the findings.
        """)
        st.subheader("LLM Configuration")
        st.write(f"Using `pydantic-ai` with `{settings.LLM_MODEL_NAME}`")
        st.warning(
            "Ensure your `OPENAI_API_KEY` environment variable is set or configure `pydantic-ai`."
        )

    if not st.session_state.initialized:
        with st.spinner(
            "Initializing the Learning Path Assistant (Loading data, setting up DB and LLM)..."
        ):
            try:
                df = load_competency_data()
                model, client = init_model_and_db()
                count = setup_vector_db(
                    client, model, df, collection_name=settings.QDRANT_COLLECTION_NAME
                )

                st.session_state.llm_agent = init_llm_agent()

                st.session_state.df = df
                st.session_state.model = model
                st.session_state.client = client
                st.session_state.initialized = True

                st.success(f"Assistant initialized with {count} competencies!")

            except FileNotFoundError as e:
                st.error(e)
            except Exception as e:
                st.error(f"An error occurred during initialization: {e}")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if (
        st.session_state.current_search_index >= 0
        and st.session_state.current_search_index < st.session_state.total_search_count
        and st.session_state.initialized
    ):
        competency_to_search = st.session_state.competencies[
            st.session_state.current_search_index
        ]
        searching_msg_content = format_searching_message(
            competency_to_search.name,
            st.session_state.current_search_index,
            st.session_state.total_search_count,
        )
        if not (
            st.session_state.messages
            and st.session_state.messages[-1]["role"] == "assistant"
            and st.session_state.messages[-1]["content"] == searching_msg_content
        ):
            st.session_state.messages.append(
                {"role": "assistant", "content": searching_msg_content}
            )
            with st.chat_message("assistant"):
                st.markdown(searching_msg_content)
            st.rerun()

        if st.session_state.messages[-1]["content"] == searching_msg_content:
            with st.spinner(
                f"Searching online for courses for {competency_to_search.name}..."
            ):
                courses = get_all_coniverse_courses(
                    competency_to_search.name, max_courses=settings.MAX_COURSES
                )
                st.session_state.search_results[competency_to_search.name] = courses

                st.session_state.current_search_index += 1

                st.rerun()

    if (
        st.session_state.current_search_index >= st.session_state.total_search_count
        and st.session_state.total_search_count > 0
        and st.session_state.llm_agent is not None
        and not st.session_state.final_message_added_for_current_search
    ):
        with st.chat_message("assistant"):
            with st.spinner("Generating personalized recommendations..."):
                course_message = generate_course_message_with_llm(
                    st.session_state.search_results,
                    st.session_state.competencies,
                    st.session_state.user_query,
                    st.session_state.llm_agent,
                )
                st.markdown(course_message)

        st.session_state.messages.append(
            {"role": "assistant", "content": course_message}
        )
        st.session_state.final_message_added_for_current_search = True

        st.session_state.current_search_index = -1

    if (
        st.session_state.current_search_index == -1
        and st.session_state.total_search_count == 0
        and st.session_state.user_query
        and not st.session_state.final_message_added_for_current_search
    ):
        pass

    if st.session_state.current_search_index == -1 and st.session_state.initialized:
        user_input = st.chat_input(
            "Enter a skill or interest you'd like to learn about:"
        )
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            initial_assistant_response = process_user_input(user_input)

            if not (
                st.session_state.messages
                and st.session_state.messages[-1]["role"] == "assistant"
                and st.session_state.messages[-1]["content"]
                == initial_assistant_response
            ):
                with st.chat_message("assistant"):
                    st.markdown(initial_assistant_response)
                st.session_state.messages.append(
                    {"role": "assistant", "content": initial_assistant_response}
                )

            st.rerun()


if __name__ == "__main__":
    main()
