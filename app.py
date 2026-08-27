import os
import json

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    st.error("OpenRouter API key not found. Check your .env file.")
    st.stop()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown(
    """
    <style>
        /* Main page */
        .block-container {
            max-width: 1100px;
            padding-top: 2rem;
            padding-bottom: 4rem;
        }

        /* Header */
        .hero {
            padding: 2rem 2.2rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            border: 1px solid rgba(128,128,128,0.25);
        }

        .hero h1 {
            font-size: 2.7rem;
            margin-bottom: 0.4rem;
        }

        .hero p {
            font-size: 1.1rem;
            opacity: 0.8;
            margin-bottom: 0;
        }

        /* Cards */
        .feature-card {
            padding: 1.4rem;
            border-radius: 16px;
            border: 1px solid rgba(128,128,128,0.25);
            min-height: 150px;
        }

        .feature-card h3 {
            margin-bottom: 0.5rem;
        }

        /* Result cards */
        .result-card {
            padding: 1.5rem;
            border-radius: 16px;
            border: 1px solid rgba(128,128,128,0.25);
            margin: 1rem 0;
        }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            border-right: 1px solid rgba(128,128,128,0.2);
        }

        /* Buttons */
        .stButton > button {
            border-radius: 10px;
            font-weight: 600;
            min-height: 45px;
        }

        /* Metrics */
        div[data-testid="stMetric"] {
            border: 1px solid rgba(128,128,128,0.25);
            padding: 1rem;
            border-radius: 14px;
        }

        /* Hide default menu/footer */
        #MainMenu {
            visibility: hidden;
        }

        footer {
            visibility: hidden;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "quiz" not in st.session_state:
    st.session_state.quiz = None

if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False

if "score" not in st.session_state:
    st.session_state.score = 0


# --------------------------------------------------
# HERO
# --------------------------------------------------

st.markdown(
    """
    <div class="hero">
        <h1>📚 AI Study Assistant</h1>
        <p>
            Learn concepts faster with AI-powered explanations,
            examples, and interactive quizzes.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.markdown("## ⚙️ Learning Settings")

    st.markdown("---")

    mode = st.radio(
        "Learning Mode",
        [
            "📚 Study Mode",
            "🧠 Quiz Mode",
        ],
    )

    st.markdown("---")

    subject = st.selectbox(
        "📖 Subject",
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

    difficulty = st.select_slider(
        "🎯 Difficulty",
        options=[
            "Beginner",
            "Intermediate",
            "Advanced",
        ],
        value="Beginner",
    )

    st.markdown("---")

    st.caption("AI Study Assistant")
    st.caption("Built with Python + Streamlit + OpenRouter")


# --------------------------------------------------
# STUDY MODE
# --------------------------------------------------

if mode == "📚 Study Mode":

    st.subheader("📖 Study Mode")
    st.write(
        "Ask a question and receive a structured study guide."
    )

    question = st.text_area(
        "What do you want to learn?",
        placeholder=(
            "Example: Explain standard deviation "
            "with a simple example."
        ),
        height=150,
        label_visibility="visible",
    )

    st.markdown("")

    if st.button(
        "🚀 Generate Study Guide",
        use_container_width=True,
        type="primary",
    ):

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

        with st.spinner(
            "🤖 Preparing your personalized study guide..."
        ):

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

                st.success("Your study guide is ready!")

                st.markdown(
                    f"""
                    <div class="result-card">
                    """,
                    unsafe_allow_html=True,
                )

                st.markdown(answer)

                st.markdown("</div>", unsafe_allow_html=True)

            except Exception:
                st.error(
                    "Something went wrong while contacting the AI. "
                    "Please try again."
                )


# --------------------------------------------------
# QUIZ MODE
# --------------------------------------------------

else:

    st.subheader("🧠 Quiz Mode")
    st.write(
        "Test your knowledge with an AI-generated multiple-choice quiz."
    )

    col1, col2 = st.columns([2, 1])

    with col1:

        topic = st.text_input(
            "🎯 Quiz Topic",
            placeholder="Example: Probability",
        )

    with col2:

        number_of_questions = st.number_input(
            "Questions",
            min_value=3,
            max_value=10,
            value=5,
            step=1,
        )

    st.markdown("")

    if st.button(
        "🧠 Generate Quiz",
        use_container_width=True,
        type="primary",
    ):

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

The "answer" must be the zero-based index
of the correct option.
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

                raw_answer = response.choices[0].message.content.strip()

                if raw_answer.startswith("```"):
                    raw_answer = raw_answer.replace(
                        "```json", ""
                    )
                    raw_answer = raw_answer.replace(
                        "```", ""
                    )
                    raw_answer = raw_answer.strip()

                quiz = json.loads(raw_answer)

                st.session_state.quiz = quiz
                st.session_state.quiz_submitted = False
                st.session_state.score = 0

                # Clear previous widget selections
                for key in list(st.session_state.keys()):
                    if key.startswith("question_"):
                        del st.session_state[key]

                st.rerun()

            except json.JSONDecodeError:

                st.error(
                    "The AI returned an invalid quiz format. "
                    "Please generate the quiz again."
                )

            except Exception:

                st.error(
                    "Something went wrong while creating the quiz."
                )


# --------------------------------------------------
# QUIZ DISPLAY
# --------------------------------------------------

if (
    mode == "🧠 Quiz Mode"
    and st.session_state.quiz is not None
):

    quiz = st.session_state.quiz

    st.markdown("---")

    # Quiz header
    st.markdown(
        f"""
        ### 🧠 {subject} Quiz

        **Difficulty:** {difficulty}  
        **Questions:** {len(quiz["questions"])}
        """
    )

    # Progress indicator
    answered = 0

    for i in range(len(quiz["questions"])):

        if f"question_{i}" in st.session_state:
            answered += 1

    progress = answered / len(quiz["questions"])

    st.progress(
        progress,
        text=f"{answered} of {len(quiz['questions'])} answered",
    )

    st.markdown("")

    answers = []

    # Questions
    for i, q in enumerate(quiz["questions"]):

        st.markdown(
            f"""
            <div class="result-card">
            <h3>Question {i + 1}</h3>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write(q["question"])

        selected = st.radio(
            "Choose your answer:",
            q["options"],
            key=f"question_{i}",
            label_visibility="visible",
        )

        answers.append(selected)

        st.markdown("")

    # Submit
    if st.button(
        "📊 Submit Quiz",
        use_container_width=True,
        type="primary",
    ):

        score = 0

        for i, q in enumerate(quiz["questions"]):

            correct_answer = q["options"][q["answer"]]

            if answers[i] == correct_answer:
                score += 1

        total = len(quiz["questions"])
        percentage = (score / total) * 100

        st.session_state.quiz_submitted = True
        st.session_state.score = score

        st.markdown("---")

        st.subheader("🏆 Quiz Results")

        # Result metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Score",
                f"{score}/{total}",
            )

        with col2:
            st.metric(
                "Percentage",
                f"{percentage:.0f}%",
            )

        with col3:

            if percentage >= 80:
                grade = "Excellent"
            elif percentage >= 50:
                grade = "Good"
            else:
                grade = "Keep Practicing"

            st.metric(
                "Performance",
                grade,
            )

        st.progress(
            percentage / 100,
            text=f"{percentage:.0f}% correct",
        )

        if percentage >= 80:

            st.success(
                "🎉 Excellent work! You have a strong understanding of this topic."
            )

        elif percentage >= 50:

            st.warning(
                "💪 Good effort! Review the incorrect answers and try again."
            )

        else:

            st.info(
                "📚 Keep practicing! Use Study Mode to review the topic."
            )

        # Answer review
        st.markdown("---")
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
                    f"**Correct answer:** {correct_answer}"
                )

            st.caption(q["explanation"])