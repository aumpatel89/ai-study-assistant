import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    st.error("OpenRouter API key not found. Check your .env file.")
    st.stop()

# OpenRouter client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

# Page configuration
st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="📚",
    layout="centered",
)

# Header
st.title("📚 AI Study Assistant")
st.caption("Learn smarter with AI-powered explanations and quizzes.")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")

    mode = st.radio(
        "Choose mode",
        ["📚 Study Mode", "🧠 Quiz Mode"],
    )

    subject = st.selectbox(
        "Subject",
        [
            "Mathematics",
            "Statistics",
            "Computer Science",
            "Physics",
            "Chemistry",
            "Biology",
            "General",
        ],
    )

    difficulty = st.selectbox(
        "Difficulty",
        ["Beginner", "Intermediate", "Advanced"],
    )

# Main input
question = st.text_area(
    "What do you want to learn?",
    placeholder="Example: Explain Bayes' theorem with a simple example.",
    height=150,
)

# Generate button
if st.button("🚀 Generate", use_container_width=True):

    if not question.strip():
        st.warning("Please enter a topic or question.")
        st.stop()

    if mode == "📚 Study Mode":

        prompt = f"""
You are an expert tutor.

Subject: {subject}
Difficulty: {difficulty}

Student question:
{question}

Create a clear educational response with:

## 📚 Explanation
Explain the concept clearly.

## 💡 Simple Example
Give an easy-to-understand example.

## 📝 Key Points
List the most important points.

## ❓ Practice Questions
Create three practice questions.

Use Markdown formatting.
"""

    else:

        prompt = f"""
You are an expert educational quiz creator.

Subject: {subject}
Difficulty: {difficulty}

Topic:
{question}

Create a short quiz containing 5 questions.

For each question:
- Give four multiple-choice options.
- Clearly identify the correct answer.
- Give a one-sentence explanation.

Use Markdown formatting.
"""

    with st.spinner("🤖 AI is preparing your response..."):

        try:

            response = client.chat.completions.create(
                model="openai/gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )

            answer = response.choices[0].message.content

            st.markdown("---")

            if mode == "📚 Study Mode":
                st.subheader("📖 Your Study Guide")
            else:
                st.subheader("🧠 Your Quiz")

            st.markdown(answer)

        except Exception as e:
            st.error(
                "Something went wrong while contacting the AI."
            )
            st.exception(e)