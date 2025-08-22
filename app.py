import streamlit as st
from google import genai
from google.genai import types
import json
import time
import os

# --- Configure Gemini API ---

gemini_api_key="AIzaSyBK_Bihz2b0phm37fjDERusC8TEbD0hq7A"

# Attempt to load API key from Streamlit secrets or environment variable
#try:
#    gemini_api_key = st.secrets["GEMINI_API_KEY"]
#except KeyError:
#    gemini_api_key = os.environ.get("GEMINI_API_KEY")

#if not gemini_api_key:
#    st.error("Gemini API Key not found. Please set it in `.streamlit/secrets.toml` or as an environment variable `GEMINI_API_KEY`.")
#    st.stop() # Stop the app if no API key

genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel('gemini-pro')

# --- User Profiles ---
user_profiles = {
    "Tess": {
        "age": 8,
        "interests": "cute dogs, drawing, simple stories, playing with friends, funny animals",
        "intro_message": "Hi there, future dog trainer! Get ready to show off your super smarts with questions about school subjects, all inspired by our fluffy, four-legged friends! You are paw-some! 💖"
    },
    "Mati": {
        "age": 10,
        "interests": "gymnastics, fashion, make-up, pop music, art, history, science experiments",
        "intro_message": "Hello, Superstar! Get ready to test your knowledge in subjects from the UK National Curriculum, with a twist of your favourite things! You've got this! ✨"
    }
}

# --- Session State Initialization ---
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'quiz_questions' not in st.session_state:
    st.session_state.quiz_questions = []
if 'current_question_idx' not in st.session_state:
    st.session_state.current_question_idx = 0
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = []
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'quiz_finished' not in st.session_state:
    st.session_state.quiz_finished = False
if 'show_results' not in st.session_state:
    st.session_state.show_results = False
if 'bonus_challenge_answer' not in st.session_state:
    st.session_state.bonus_challenge_answer = ""
if 'quiz_started' not in st.session_state: # New flag to indicate if questions have been generated
    st.session_state.quiz_started = False
if 'last_generated_user' not in st.session_state: # To prevent regenerating if user hasn't changed
    st.session_state.last_generated_user = None


# --- Functions for Gemini Question Generation ---
def generate_quiz_questions(user_profile):
    st.session_state.quiz_questions = [] # Clear previous questions
    st.session_state.user_answers = [] # Clear previous answers
    st.session_state.score = 0
    st.session_state.quiz_finished = False
    st.session_state.show_results = False
    st.session_state.current_question_idx = 0
    st.session_state.bonus_challenge_answer = ""
    st.session_state.quiz_started = False # Reset quiz started state

    age = user_profile["age"]
    interests = user_profile["interests"]
    
    prompt = f"""
    You are creating a 10-question quiz for an {age}-year-old girl.
    The quiz should cover aspects of the UK National Curriculum (e.g., English, Maths, Science, History, Art, Music), but be highly tailored to her interests: {interests}.
    Each question must be multiple-choice with exactly 4 options.
    The correct answer MUST be one of the options provided.
    The tone should be encouraging, fun, and appropriate for her age.
    The output MUST be a JSON array of 10 question objects. Each object must have the following keys:
    - 'question': The quiz question as a string.
    - 'options': A JSON array of 4 string options.
    - 'answer': The correct answer string (must be one of the options).
    - 'subject': The UK National Curriculum subject (e.g., 'English', 'Maths', 'Science', 'History', 'Art', 'Music').

    Example format:
    [
      {{
        "question": "What is 2 + 2?",
        "options": ["3", "4", "5", "6"],
        "answer": "4",
        "subject": "Maths"
      }},
      {{
        "question": "Which animal barks?",
        "options": ["Cat", "Dog", "Bird", "Fish"],
        "answer": "Dog",
        "subject": "Science"
      }}
    ]

    Generate 10 questions now based on the profile:
    Age: {age}
    Interests: {interests}
    """
    
    with st.spinner("Generating amazing new questions for you... Please wait a moment! ✨"):
        try:
            response = model.generate_content(prompt)
            # st.write(response.text) # For debugging Gemini's raw output
            quiz_data = json.loads(response.text)
            
            # Basic validation of the generated data
            if not isinstance(quiz_data, list) or len(quiz_data) != 10:
                raise ValueError("Gemini did not return a list of 10 questions.")
            for q in quiz_data:
                if not all(k in q for k in ["question", "options", "answer", "subject"]) or \
                   not isinstance(q["options"], list) or len(q["options"]) != 4 or \
                   q["answer"] not in q["options"]:
                    raise ValueError(f"Invalid question format detected: {q}")

            st.session_state.quiz_questions = quiz_data
            st.session_state.user_answers = [None] * len(quiz_data)
            st.session_state.quiz_started = True
            st.session_state.last_generated_user = user_profile # Store user whose questions were generated
            st.success("Questions loaded! Let's play! 🎉")
            st.rerun() # Rerun to display the first question
        except json.JSONDecodeError:
            st.error("Failed to decode quiz questions from Gemini. Please try again.")
            st.write("Gemini's raw output (for debugging):")
            st.code(response.text)
        except ValueError as e:
            st.error(f"Error validating quiz questions: {e}. Please try generating again.")
            st.write("Gemini's raw output (for debugging):")
            st.code(response.text)
        except Exception as e:
            st.error(f"An unexpected error occurred while generating questions: {e}. Please try again.")
            st.write("Consider trying again or checking your API key and network connection.")


# --- Functions for Quiz Navigation ---
def next_question():
    if st.session_state.current_question_idx < len(st.session_state.quiz_questions) - 1:
        st.session_state.current_question_idx += 1
    else:
        st.session_state.quiz_finished = True
        st.session_state.show_results = True # Automatically show results when quiz finishes

def previous_question():
    if st.session_state.current_question_idx > 0:
        st.session_state.current_question_idx -= 1

def restart_quiz():
    st.session_state.current_question_idx = 0
    st.session_state.user_answers = [None] * len(st.session_state.quiz_questions)
    st.session_state.score = 0
    st.session_state.quiz_finished = False
    st.session_state.show_results = False
    st.session_state.bonus_challenge_answer = ""
    st.session_state.quiz_started = False # Allow regenerating questions
    st.session_state.quiz_questions = [] # Clear questions on full restart
    st.session_state.last_generated_user = None
    st.rerun() # Rerun to go back to user selection


def calculate_score():
    correct_answers_count = 0
    for i, q in enumerate(st.session_state.quiz_questions):
        if st.session_state.user_answers[i] == q["answer"]:
            correct_answers_count += 1
    st.session_state.score = correct_answers_count

# --- Streamlit App Layout ---

st.set_page_config(page_title="Personalized Fun Quiz!", page_icon="✨")

# Custom CSS for a touch of glam and ADHD-friendly spacing
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5em;
        color: #FF69B4; /* Hot Pink */
        text-align: center;
        margin-bottom: 30px;
        text-shadow: 2px 2px 4px #ccc;
    }
    .subheader {
        font-size: 1.5em;
        color: #8A2BE2; /* Blue Violet */
        margin-top: 20px;
        margin-bottom: 15px;
    }
    .question-box {
        background-color: #FFF0F5; /* Lavender Blush */
        border-left: 5px solid #FF1493; /* Deep Pink */
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 25px;
    }
    .stRadio > label {
        font-size: 1.1em;
        margin-bottom: 10px;
    }
    .stRadio div[role="radiogroup"] {
        margin-top: 10px;
        margin-bottom: 15px;
    }
    .stRadio div[data-baseweb="radio"] {
        margin-bottom: 8px; /* Spacing between radio options */
    }
    .stButton > button {
        background-color: #FFD700; /* Gold */
        color: black;
        font-weight: bold;
        padding: 10px 20px;
        border-radius: 8px;
        border: none;
        cursor: pointer;
        transition: all 0.2s ease-in-out;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
    }
    .stButton > button:hover {
        background-color: #FFA500; /* Orange */
        transform: translateY(-2px);
    }
    .score-display {
        font-size: 1.8em;
        color: #32CD32; /* Lime Green */
        font-weight: bold;
        text-align: center;
        margin-top: 30px;
    }
    .feedback-correct {
        color: green;
        font-weight: bold;
    }
    .feedback-incorrect {
        color: red;
        font-weight: bold;
    }
    .explanation {
        font-style: italic;
        color: #555;
        margin-top: 5px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)


st.markdown("<h1 class='main-header'>The Personalized Power Quiz! 🎉</h1>", unsafe_allow_html=True)

# --- User Selection ---
if not st.session_state.quiz_started:
    st.write("Hello! Let's choose who is playing today:")
    selected_user_name = st.radio(
        "Who are you?",
        list(user_profiles.keys()),
        key="user_selector",
        index=list(user_profiles.keys()).index(st.session_state.current_user) if st.session_state.current_user else 0
    )
    
    # Update current_user in session state
    if selected_user_name != st.session_state.current_user:
        st.session_state.current_user = selected_user_name
        # If user changes, reset quiz state to allow new question generation
        restart_quiz() # This will rerun the app and reset, so current_user selection is preserved and new questions can be generated.

    st.markdown(f"**Welcome, {st.session_state.current_user}!**")
    st.markdown(user_profiles[st.session_state.current_user]["intro_message"], unsafe_allow_html=True)

    if st.button(f"Generate New Quiz for {st.session_state.current_user}!", key="generate_quiz_button"):
        generate_quiz_questions(user_profiles[st.session_state.current_user])
        # The generate_quiz_questions function will handle rerunning if successful

# --- Quiz Display ---
if st.session_state.quiz_started and not st.session_state.quiz_finished:
    if not st.session_state.quiz_questions:
        st.warning("No questions loaded. Please select a user and generate a quiz.")
    else:
        current_q = st.session_state.quiz_questions[st.session_state.current_question_idx]

        st.markdown(f"<div class='question-box'>", unsafe_allow_html=True)
        st.markdown(f"<p class='subheader'>Question {st.session_state.current_question_idx + 1} of {len(st.session_state.quiz_questions)} - {current_q['subject']}</p>", unsafe_allow_html=True)
        
        with st.form(key=f"question_form_{st.session_state.current_question_idx}"):
            st.markdown(f"**{current_q['question']}**")
            
            # Determine the initial index for the radio button, handling None
            current_answer_idx = 0
            if st.session_state.user_answers[st.session_state.current_question_idx] in current_q["options"]:
                current_answer_idx = current_q["options"].index(st.session_state.user_answers[st.session_state.current_question_idx])
            elif st.session_state.user_answers[st.session_state.current_question_idx] is None:
                 # If no answer yet, set index to -1 so no option is pre-selected.
                 # Streamlit's st.radio defaults to the first option if index is 0 and no value,
                 # so setting it explicitly if an answer exists, otherwise it will display the default.
                 # For a clean unselected state, we need to carefully manage this, or just let it default and user picks.
                 # For simplicity here, if no answer, let it default to 0 and user can change.
                 pass # keep current_answer_idx at 0 if no answer yet

            user_choice = st.radio(
                "Select your answer:",
                current_q["options"],
                index=current_answer_idx if st.session_state.user_answers[st.session_state.current_question_idx] is not None else 0, # Default to first if not answered
                key=f"q_{st.session_state.current_question_idx}_radio",
                horizontal=True
            )
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.session_state.current_question_idx > 0:
                    st.form_submit_button("⬅️ Previous", on_click=previous_question)
            with col2:
                # Use a specific emoji for each user if desired, or keep generic
                submit_emoji = "🐾" if st.session_state.current_user == "Tess" else "✨"
                submitted = st.form_submit_button(f"Submit Answer & Next {submit_emoji}")

            if submitted:
                st.session_state.user_answers[st.session_state.current_question_idx] = user_choice
                calculate_score()
                next_question()
                st.rerun()
        
        st.markdown(f"</div>", unsafe_allow_html=True)

# --- Quiz Results ---
elif st.session_state.quiz_finished:
    st.markdown("<h2 class='main-header'>Quiz Complete! 🎉</h2>", unsafe_allow_html=True)
    st.markdown(f"<div class='score-display'>Your final score: {st.session_state.score} out of {len(st.session_state.quiz_questions)}!</div>", unsafe_allow_html=True)

    st.write("---")
    st.markdown("### Review Your Answers:")
    for i, q in enumerate(st.session_state.quiz_questions):
        st.markdown(f"**Question {i+1}:** {q['question']}")
        user_ans = st.session_state.user_answers[i]
        correct_ans = q['answer']

        if user_ans == correct_ans:
            st.markdown(f"<p class='feedback-correct'>✅ Your Answer: {user_ans}</p>", unsafe_allow_html=True)
        else:
            st.markdown(f"<p class='feedback-incorrect'>❌ Your Answer: {user_ans if user_ans else 'Not answered'}</p>", unsafe_allow_html=True)
            st.markdown(f"<p class='feedback-correct'>Correct Answer: {correct_ans}</p>", unsafe_allow_html=True)
        st.write("")

    st.markdown("---")
    st.markdown("### Bonus Challenge (Just for fun!)")
    if st.session_state.current_user == "Tess":
        st.write("If you could design the most amazing, super-fun dog park in the world, what exciting things would it have for all the cute pups?")
    elif st.session_state.current_user == "Mati":
        st.write("If you could combine gymnastics and pop music into one amazing performance, what would it look like? Describe it in one exciting sentence! 🌟")

    st.session_state.bonus_challenge_answer = st.text_area(
        "Your amazing idea:",
        value=st.session_state.bonus_challenge_answer,
        key="bonus_challenge_text_area",
        height=100
    )

    st.button("Start New Quiz! 🚀", on_click=restart_quiz)
