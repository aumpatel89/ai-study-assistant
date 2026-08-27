import os
import json

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

# -------------------------
# STUDY MODE
# -------------------------

if mode == "📚 Study Mode":

    question = st.text_area(
        "What do you want to learn?",
        placeholder="Example: Explain Bayes' theorem with a simple example.",
        height=150,
    )

    if st.button("🚀 Generate Study Guide", use_container_width=True):

        if not question.strip():
            st.warning("Please enter a topic or question.")
            st.stop()

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

        with st.spinner("🤖 Preparing your study guide..."):

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
                st.subheader("📖 Your Study Guide")
                st.markdown(answer)

            except Exception as e:
                st.error("Something went wrong while contacting the AI.")
                st.exception(e)


# -------------------------
# QUIZ MODE
# -------------------------

else:

    topic = st.text_input(
        "What topic should the quiz cover?",
        placeholder="Example: Probability",
    )

    number_of_questions = st.slider(
        "Number of questions",
        min_value=3,
        max_value=10,
        value=5,
    )

    if st.button("🧠 Generate Quiz", use_container_width=True):

        if not topic.strip():
            st.warning("Please enter a topic.")
            st.stop()

        prompt = f"""
Create a multiple-choice quiz.

Subject: {subject}
Difficulty: {difficulty}
Topic: {topic}

Create exactly {number_of_questions} questions.

Return ONLY valid JSON using this structure:

{{
    "questions": [
        {{
            "question": "Question text",
            "options": [
                "Option A",
                "Option B",
                "Option C",
                "Option D"
            ],
            "answer": 0,
            "explanation": "Short explanation"
        }}
    ]
}}

The "answer" must be the zero-based index of the correct option.
"""

        with st.spinner("🤖 Creating your quiz..."):

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

                raw_answer = response.choices[0].message.content

                # Remove possible Markdown code fences
                raw_answer = raw_answer.strip()

                if raw_answer.startswith("```"):
                    raw_answer = raw_answer.replace("```json", "")
                    raw_answer = raw_answer.replace("```", "")
                    raw_answer = raw_answer.strip()

                quiz = json.loads(raw_answer)

                st.session_state.quiz = quiz
                st.session_state.quiz_submitted = False

            except json.JSONDecodeError:
                st.error(
                    "The AI returned an invalid quiz format. "
                    "Please try generating the quiz again."
                )

            except Exception as e:
                st.error("Something went wrong while creating the quiz.")
                st.exception(e)


# -------------------------
# DISPLAY QUIZ
# -------------------------

if mode == "🧠 Quiz Mode" and "quiz" in st.session_state:

    quiz = st.session_state.quiz

    st.markdown("---")
    st.subheader("🧠 Your Quiz")

    answers = []

    for i, q in enumerate(quiz["questions"]):

        st.markdown(f"### Question {i + 1}")

        st.write(q["question"])

        selected = st.radio(
            "Choose an answer:",
            q["options"],
            key=f"question_{i}",
        )

        answers.append(selected)

    if st.button("📊 Submit Quiz", use_container_width=True):

        score = 0

        for i, q in enumerate(quiz["questions"]):

            correct_answer = q["options"][q["answer"]]

            if answers[i] == correct_answer:
                score += 1

        total = len(quiz["questions"])

        st.session_state.quiz_submitted = True
        st.session_state.score = score

        st.markdown("---")

        st.subheader("🏆 Quiz Results")

        percentage = (score / total) * 100

        st.metric(
            "Your Score",
            f"{score}/{total}",
        )

        st.progress(percentage / 100)

        if percentage >= 80:
            st.success("Excellent work! 🎉")

        elif percentage >= 50:
            st.warning("Good effort! Keep practicing. 💪")

        else:
            st.error("Keep studying and try again! 📚")

        st.subheader("📝 Answer Review")

        for i, q in enumerate(quiz["questions"]):

            correct_answer = q["options"][q["answer"]]

            if answers[i] == correct_answer:
                st.success(
                    f"Question {i + 1}: Correct ✅"
                )
            else:
                st.error(
                    f"Question {i + 1}: Incorrect ❌"
                )

                st.write(
                    f"Correct answer: **{correct_answer}**"
                )

            st.caption(q["explanation"])