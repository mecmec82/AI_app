import streamlit as st
from google import generativeai as genai # Corrected import for genai
from pydantic import BaseModel
import json
import re

# Define the Pydantic model for quiz questions
class QuizQuestion(BaseModel):
    question: str
    options: list[str] # Ensure options is a list of strings
    answer: str
    explanation: str

# Function to call the LLM and generate the quiz
@st.cache_data(show_spinner="Generating your personalized quiz...")
def LLM_call():
    # IMPORTANT: For a production app, use st.secrets or environment variables for API keys.
    # st.secrets["GOOGLE_API_KEY"]
    # For this example, we'll use the hardcoded key from your original code.
    # Replace "AIzaSyBK_Bihz2b0phm37fjDERusC8TEbD0hq7A" with your actual API key
    # or better, configure it via st.secrets.toml.
    api_key = "AIzaSyBK_Bihz2b0phm37fjDERusC8TEbD0hq7A" 
    
    if not api_key:
        st.error("Google API Key not found. Please provide your API key.")
        return None

    try:
        genai.configure(api_key=api_key) # Configure the API key here
        client = genai.GenerativeModel("gemini-1.5-flash") # Corrected model name

        response = client.generate_content(
            contents=f"""
            Give me a 10 question quiz that covers relative aspects of the UK national curriculum for a 10 year old girl.
            The student loves gymnastics, fashion, make-up and pop music.
            Ensure the options for each question are unique and distinct.
            """,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json",
                response_schema=list[QuizQuestion]
            ),
        )
        
        # Accessing text from the response
        json_output = response.text
        
        # Ensure the output is clean JSON by removing markdown fences if present
        cleaned_json_output = json_output.strip().strip('```json').strip('```')
        
        quiz_data_raw = json.loads(cleaned_json_output)
        
        # Validate and convert raw dictionary data to Pydantic models
        quiz_list = [QuizQuestion(**q) for q in quiz_data_raw]
        return quiz_list
    except Exception as e:
        st.error(f"Failed to generate quiz: {e}")
        st.info("Please check your API key and try again. Also ensure the model is accessible.")
        return None

##############  STREAMLIT APP #####################

st.title("Personalized Quiz App with Gemini")
st.markdown("---")

# Initialize session state variables if they don't exist
if 'quiz_data' not in st.session_state:
    st.session_state.quiz_data = None
if 'current_question_index' not in st.session_state:
    st.session_state.current_question_index = 0
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = []
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'quiz_started' not in st.session_state:
    st.session_state.quiz_started = False

# --- Quiz Generation Section ---
if not st.session_state.quiz_started:
    st.info("Click the button below to generate a new quiz!")
    if st.button("Generate New Quiz"):
        st.session_state.quiz_data = LLM_call()
        if st.session_state.quiz_data:
            st.session_state.current_question_index = 0
            st.session_state.user_answers = [None] * len(st.session_state.quiz_data)
            st.session_state.score = 0
            st.session_state.quiz_started = True
            st.rerun() # Rerun to start displaying questions
elif st.session_state.quiz_data is None:
    st.warning("Quiz generation failed or no quiz data. Please try generating the quiz again.")
    st.session_state.quiz_started = False # Allow regenerating if an error occurred

# --- Quiz Display Section ---
if st.session_state.quiz_started and st.session_state.quiz_data:
    quiz_data = st.session_state.quiz_data
    total_questions = len(quiz_data)
    current_index = st.session_state.current_question_index

    if current_index < total_questions:
        # Display current question
        question_obj = quiz_data[current_index]
        
        st.header(f"Question {current_index + 1}/{total_questions}")
        st.write(f"**{question_obj.question}**")

        # Use st.radio for options
        selected_option = st.radio(
            "Choose your answer:",
            question_obj.options,
            key=f"q_{current_index}" # Unique key for each radio button
        )

        # Update user's answer in session state
        st.session_state.user_answers[current_index] = selected_option

        col1, col2 = st.columns([1, 4]) # Create columns for button alignment
        with col1:
            if st.button("Next Question", key="next_q_button"):
                # Check answer and update score (optional, can be done at the end)
                # We'll save the check for the end to keep the flow clean
                
                if current_index < total_questions - 1:
                    st.session_state.current_question_index += 1
                    st.rerun()
                else:
                    # Last question, proceed to results
                    st.session_state.current_question_index += 1 # Increment to indicate quiz finished
                    st.rerun()
    else:
        # --- Results Section ---
        st.header("Quiz Completed!")
        st.markdown("---")

        correct_answers_count = 0
        quiz_results = []

        for i, q_obj in enumerate(quiz_data):
            user_ans = st.session_state.user_answers[i]
            is_correct = (user_ans == q_obj.answer)
            if is_correct:
                correct_answers_count += 1
            
            quiz_results.append({
                "question": q_obj.question,
                "user_answer": user_ans,
                "correct_answer": q_obj.answer,
                "is_correct": is_correct,
                "explanation": q_obj.explanation
            })
        
        st.session_state.score = correct_answers_count
        st.success(f"You scored {st.session_state.score} out of {total_questions}!")

        st.subheader("Review Your Answers:")
        for i, result in enumerate(quiz_results):
            st.markdown(f"**Question {i + 1}:** {result['question']}")
            st.write(f"Your Answer: {result['user_answer']}")
            if result['is_correct']:
                st.markdown(f"<p style='color:green;'>**Correct!**</p>", unsafe_allow_html=True)
            else:
                st.markdown(f"<p style='color:red;'>**Incorrect.** The correct answer was: {result['correct_answer']}</p>", unsafe_allow_html=True)
            st.info(f"Explanation: {result['explanation']}")
            st.markdown("---")

        if st.button("Start New Quiz"):
            st.session_state.quiz_data = None
            st.session_state.current_question_index = 0
            st.session_state.user_answers = []
            st.session_state.score = 0
            st.session_state.quiz_started = False
            st.rerun()
