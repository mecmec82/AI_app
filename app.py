import streamlit as st
from google import genai
from google.generativeai import types
from pydantic import BaseModel, Field, ValidationError
from typing import List
import json
import os # Make sure os is imported for environment variables

# --- Pydantic Model for Quiz Questions ---
class QuizQuestion(BaseModel):
    question: str = Field(description="The quiz question for the user.")
    options: List[str] = Field(description="A list of 4 possible answer options.")
    answer: str = Field(description="The correct answer, which must be one of the options.")
    subject: str = Field(description="The UK National Curriculum subject covered by the question (e.g., 'English', 'Maths', 'Science', 'History', 'Art', 'Music').")
    explanation: str = Field(description="A brief explanation of why the answer is correct.")

# --- Configure Gemini API ---
# Attempt to load API key from Streamlit secrets or environment variable
try:
    gemini_api_key = st.secrets["GEMINI_API_KEY"]
except KeyError:
    gemini_api_key = os.environ.get("GEMINI_API_KEY")

if not gemini_api_key:
    st.error("Gemini API Key not found. Please set it in `.streamlit/secrets.toml` or as an environment variable `GEMINI_API_KEY`.")
    st.stop() # Stop the app if no API key

# Initialize the Gemini client using the google-ai-generativelanguage library's Client
try:
    client = genai.Client(api_key=gemini_api_key)
except Exception as e:
    st.error(f"Failed to initialize Gemini client: {e}. Please check your API key.")
    st.stop()

# --- User Profiles ---
user_profiles = {
    "Tess": {
        "age": 8,
        "interests": "cute dogs, drawing, simple stories, playing with friends, funny animals, cuddly toys",
        "intro_message": "Hi there, future dog trainer! Get ready to show off your super smarts with questions about school subjects, all inspired by our fluffy, four-legged friends! You are paw-some! 💖"
    },
    "Mati": {
        "age": 10,
        "interests": "gymnastics, fashion, make-up, pop music, art, history, science experiments, glitter, sparkling things",
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
if 'quiz_started' not in st.session_state:
    st.session_state.quiz_started = False
if 'last_generated_user_profile' not in st.session_state: # To prevent regenerating if user hasn't changed
    st.session_state.last_generated_user_profile = None

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
    For each question, also provide a short, simple explanation for the correct answer.

    Generate 10 questions now based on the profile:
    Age: {age}
    Interests: {interests}
    """

    with st.spinner("Generating amazing new questions for you... Please wait a moment! ✨"):
        try:
            # Using client.models.generate_content with response_mime_type and response_schema
            response = client.models.generate_content(
                model="gemini-1.5-flash-latest", # Using a more recent flash model as per current best practices
                contents=prompt,
                generation_config=types.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=types.StructType(
                        properties={
                            "quiz": types.ArrayType(
                                element_type=types.StructType(
                                    properties={
                                        "question": types.SchemaProperty(type=types.Type.STRING),
                                        "options": types.SchemaProperty(type=types.Type.ARRAY, items=types.SchemaProperty(type=types.Type.STRING)),
                                        "answer": types.SchemaProperty(type=types.Type.STRING),
                                        "subject": types.SchemaProperty(type=types.Type.STRING),
                                        "explanation": types.SchemaProperty(type=types.Type.STRING),
                                    }
                                )
                            )
                        }
                    )
                )
            )

            # The response.text should already be a JSON string
            # It comes wrapped in {"quiz": [...]} because of the outer StructType
            raw_json_output = json.loads(response.text)
            
            # Extract the list of questions
            quiz_data_dicts = raw_json_output.get("quiz", [])

            # Validate each question using Pydantic
            validated_questions = []
            for q_dict in quiz_data_dicts:
                try:
                    # Convert Pydantic model to dictionary for consistent app usage
                    validated_questions.append(QuizQuestion(**q_dict).model_dump())
                except ValidationError as e:
                    st.warning(f"Skipping malformed question from API: {e}. Check API output format.")
                    st.json(q_dict) # Display the problematic dict for debugging

            if not validated_questions:
                raise ValueError("No valid questions were generated by the API.")
            
            st.session_state.quiz_questions = validated_questions
            st.session_state.user_answers = [None] * len(validated_questions)
            st.session_state.quiz_started = True
            st.session_state.last_generated_user_profile = user_profile # Store user profile used
            st.success("Questions loaded! Let's play! 🎉")
            st.rerun() # Rerun to display the first question

        except json.JSONDecodeError as e:
            st.error(f"Failed to decode quiz questions from Gemini: {e}. Raw response: {response.text}")
        except ValidationError as e:
            st.error(f"Generated quiz questions do not match the expected format (Pydantic validation error): {e}")
        except ValueError as e:
            st.error(f"Error with generated quiz data: {e}. Please try again.")
        except Exception as e:
            st.error(f"An unexpected error occurred while generating questions: {e}. Please try again.")
            st.write("Consider checking your API key and network connection.")

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
    st.session_state.user_answers = [] # Reset answers
    st.session_state.score = 0
    st.session_state.quiz_finished = False
    st.session_state.show_results = False
    st.session_state.bonus_challenge_answer = ""
    st.session_state.quiz_started = False # Allow regenerating questions
    st.session_state.quiz_questions = [] # Clear questions on full restart
    st.session_state.last_generated_user_profile = None # Clear last generated user
    st.rerun() # Rerun to go back to user selection


def calculate_score():
    correct_answers_count = 0
    for i, q in enumerate(st.session_state.quiz_questions):
        if st.session_state.user_answers[i] == q["answer"]:
            correct_answers_count += 1
    st.session_state.score = correct_answers_count

# --- Streamlit App Layout ---

st.set_page_config(page_title="Personalized Power Quiz!", page_icon="🎉")

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
        padding-left: 10px;
        border-left: 3px solid #eee;
    }
    </style>
    """, unsafe_allow_html=True)


st.markdown("<h1 class='main-header'>The Personalized Power Quiz! 🎉</h1>", unsafe_allow_html=True)

# --- User Selection ---
if not st.session_state.quiz_started:
    st.write("Hello! Let's choose who is playing today:")
    
    # Get current user name or default to first if not set
    current_user_name = st.session_state.current_user if st.session_state.current_user else list(user_profiles.keys())[0]

    selected_user_name = st.radio(
        "Who are you?",
        list(user_profiles.keys()),
        key="user_selector",
        index=list(user_profiles.keys()).index(current_user_name)
    )
    
    if selected_user_name != st.session_state.current_user:
        st.session_state.current_user = selected_user_name
        # If user changes, force a reset to regenerate questions
        restart_quiz()
        st.experimental_rerun() # Force rerun to pick up new user profile
        
    st.markdown(f"**Welcome, {st.session_state.current_user}!**")
    st.markdown(user_profiles[st.session_state.current_user]["intro_message"], unsafe_allow_html=True)

    if st.button(f"Generate New Quiz for {st.session_state.current_user}!", key="generate_quiz_button"):
        generate_quiz_questions(user_profiles[st.session_state.current_user])
        # Function handles rerunning on success
    
    # If questions were generated for the selected user, move to the quiz display
    if st.session_state.quiz_started and st.session_state.last_generated_user_profile == user_profiles[st.session_state.current_user]:
        st.empty() # Clear the user selection area before moving to quiz


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
            
            current_answer_idx = -1 # Default to no option selected
            if st.session_state.current_question_idx < len(st.session_state.user_answers) and \
               st.session_state.user_answers[st.session_state.current_question_idx] in current_q["options"]:
                current_answer_idx = current_q["options"].index(st.session_state.user_answers[st.session_state.current_question_idx])
            
            user_choice = st.radio(
                "Select your answer:",
                current_q["options"],
                index=current_answer_idx,
                key=f"q_{st.session_state.current_question_idx}_radio",
                horizontal=True
            )
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.session_state.current_question_idx > 0:
                    st.form_submit_button("⬅️ Previous", on_click=previous_question)
            with col2:
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
        
        # Display the explanation
        if 'explanation' in q and q['explanation']:
            st.markdown(f"<p class='explanation'>**Explanation:** {q['explanation']}</p>", unsafe_allow_html=True)
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
