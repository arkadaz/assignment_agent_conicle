import streamlit as st
from pydantic_ai import Agent

import settings
from models import Competency


def init_llm_agent():
    try:
        llm_agent = Agent(
            settings.LLM_MODEL_NAME,
            deps_type=None,
            system_prompt=(
                "You are a helpful and friendly Learning Path Assistant. "
                "Your goal is to provide course recommendations based on the data provided to you. "
                "Format your response using Markdown, grouping courses by competency and explaining relevance."
                "Be concise and encouraging."
            ),
        )
        return llm_agent
    except Exception as e:
        st.error(
            f"Failed to initialize LLM Agent. Please check your configuration and API access (e.g., OPENAI_API_KEY): {e}"
        )
        return None


def generate_course_message_with_llm(
    search_results: dict,
    competencies: list[Competency],
    user_query: str,
    llm_agent: Agent,
):
    if llm_agent is None:
        return "LLM Agent is not initialized. Cannot generate recommendations."

    if not competencies:
        return "I couldn't find any competencies or courses this time."

    data_for_llm = f"User Query: {user_query}\n\nRelevant Competencies:\n"
    for i, comp in enumerate(competencies):
        data_for_llm += (
            f"- Competency {i + 1}: {comp.name}\n  Description: {comp.description}\n"
        )

    data_for_llm += "\nSearch Results (Competency -> List of Course Titles):\n"
    found_any_courses_in_results = False
    for comp in competencies:
        if (
            comp.name in search_results
            and search_results[comp.name]
            and search_results[comp.name] != ["No courses found."]
        ):
            valid_courses_for_comp = [
                course
                for course in search_results[comp.name]
                if course
                and course != "No courses found."
                and not course.startswith("Error")
            ]
            if valid_courses_for_comp:
                data_for_llm += f"- {comp.name}:\n"
                for course in valid_courses_for_comp:
                    data_for_llm += f"  - {course}\n"
                found_any_courses_in_results = True

    if not found_any_courses_in_results:
        return "I found some relevant competencies, but couldn't find specific courses for them at this time. The course search might have failed or returned no results."

    prompt = f"""
You are a helpful Learning Path Assistant. Your task is to generate a course recommendation message for a user based on their original interest, a list of relevant competencies, and a list of courses found for each competency.

The user's original interest was: "{user_query}"

Here is the data containing the relevant competencies and the course titles found for each (competencies with no courses found are not listed in the search results section):

{data_for_llm}

IMPORTANT: Carefully analyze each course title and DISCARD any courses that don't seem directly related to the competency or the user's query. If a course title doesn't clearly indicate relevance to the competency or user's interest, do not include it in your recommendations.

Please format the response as a user-friendly message using Markdown.
Start with a welcoming introduction like "Here are some course recommendations based on your interests:".
For each competency listed in the "Search Results" section above, create a dedicated section using a Markdown heading (e.g., "## Courses for [Competency Name]").
Under each competency heading, list ONLY the course titles that are truly relevant to both the competency and the user's query. Format each course title in bold markdown (**Course Title**).
Below each bold course title, include a brief sentence explaining its relevance. Mention the competency name and how it relates to the user's original interest ("{user_query}"). For example: "*This course covers topics related to [Competency Name] that align with your interest in {user_query}.*"
Ensure you only include competencies and courses that were successfully found, provided in the data above, AND are directly relevant.
After listing all the courses, conclude the message by asking the user if they would like to explore any of these competencies in more detail, or would like to search for something else.

If after filtering, you find that none of the courses are truly relevant, state: "I found some competencies related to your interest, but couldn't find specific courses that are directly relevant at this time. Would you like to try a different search with more specific keywords?"

Ensure the final output uses correct Markdown syntax for headings, bold text, and italics.
"""

    try:
        result = llm_agent.run_sync(prompt)
        return result.output
    except Exception as e:
        st.error(f"Error generating message with LLM: {e}")
        return "Sorry, I encountered an error while trying to generate the course recommendations."
