import os
import time
import streamlit as st
from dotenv import load_dotenv
from google import genai

# ==========================================
# LOAD ENVIRONMENT
# ==========================================
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

# ==========================================
# PAGE SETTINGS
# ==========================================
st.set_page_config(
    page_title="AI Learning Assistant",
    page_icon="🎓",
    layout="wide"
)

# ==========================================
# TITLE
# ==========================================
st.title("🎓 The Role of ChatGPT in Learning")
st.write("An AI-powered learning assistant for students.")
st.divider()

# ==========================================
# API KEY CHECK
# ==========================================
if not api_key:
    st.error("❌ GEMINI_API_KEY is missing in the .env file.")
    st.stop()

# ==========================================
# GEMINI CLIENT
# ==========================================
try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"❌ Gemini client error: {e}")
    st.stop()

# ==========================================
# SIDEBAR
# ==========================================
st.sidebar.header("📚 Learning Tools")

option = st.sidebar.selectbox(
    "Choose a feature",
    [
        "AI Tutor",
        "Study Notes",
        "Quiz Generator",
        "Summarizer",
        "Programming Helper"
    ]
)

st.sidebar.divider()

st.sidebar.write("Selected Tool:")
st.sidebar.success(option)

# ==========================================
# TOPIC INPUT
# ==========================================
st.subheader("📝 Enter Your Topic")

topic = st.text_area(
    "Topic or Question",
    placeholder="Example: Java inheritance",
    height=100
)

# ==========================================
# CREATE PROMPT
# ==========================================
def create_prompt(tool, topic):

    if tool == "AI Tutor":
        return f"""
Explain {topic} to a student.

Use:
- Simple definition
- Important points
- One easy example
- Short conclusion

Keep the answer simple and clear.
"""

    elif tool == "Study Notes":
        return f"""
Create short study notes about {topic}.

Include:
- Definition
- Important points
- Key facts
- Example
- Conclusion

Use headings and bullet points.
"""

    elif tool == "Quiz Generator":
        return f"""
Create 5 MCQ questions about {topic}.

Each question must contain:
A. option
B. option
C. option
D. option

Show the correct answer after each question.
Give a short explanation.
"""

    elif tool == "Summarizer":
        return f"""
Give a short and simple summary of {topic}.

Use easy language.
Include only the most important points.
"""

    else:
        return f"""
Explain {topic} as a programming concept.

Include:
- Simple explanation
- Small code example
- Step-by-step explanation

Keep the code beginner-friendly.
"""

# ==========================================
# GEMINI STREAMING FUNCTION
# ==========================================
def generate_answer(prompt):

    max_attempts = 2

    for attempt in range(1, max_attempts + 1):

        try:

            stream = client.interactions.create(
                model="gemini-3.8-flash",
                input=prompt,
                generation_config={
                    "thinking_level": "low"
                },
                stream=True
            )

            return stream

        except Exception as e:

            error_message = str(e).lower()

            if "503" in error_message or "service_unavailable" in error_message:

                if attempt < max_attempts:
                    time.sleep(1)
                else:
                    raise RuntimeError(
                        "Gemini is temporarily busy. "
                        "Please click Generate again."
                    )

            else:
                raise e

# ==========================================
# GENERATE BUTTON
# ==========================================
if st.button("🚀 Generate", use_container_width=True):

    if not topic.strip():

        st.warning("⚠️ Please enter a topic.")

    else:

        prompt = create_prompt(option, topic)

        try:

            with st.spinner("🤖 Connecting to Gemini..."):

                stream = generate_answer(prompt)

            st.success("✅ Answer generated!")

            st.subheader("📚 Learning Result")

            # Empty area for streaming output
            result_box = st.empty()

            answer = ""

            # Receive Gemini response chunk by chunk
            for event in stream:

                if event.event_type == "step.delta":

                    if event.delta.type == "text":

                        text_chunk = event.delta.text

                        if text_chunk:
                            answer += text_chunk
                            result_box.markdown(answer)

            # If nothing was received
            if not answer:
                st.warning("No answer was returned. Please try again.")

        except Exception as e:

            st.error(f"❌ Error: {e}")

# ==========================================
# FOOTER
# ==========================================
st.divider()

st.caption(
    "🎓 AI Learning Assistant | "
    "The Role of ChatGPT in Learning"
)