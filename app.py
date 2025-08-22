import streamlit as st

# --- Quiz Data (Updated for 8-year-old and cute dogs!) ---
quiz_questions = [
    {
        "question": "Your dog, Waffle, just did an amazing trick! You want to write about it with lots of excitement. Which punctuation mark is missing from this sentence? 'Waffle did it Wow'",
        "options": [", (Comma)", ". (Full stop)", "! (Exclamation mark)", "? (Question mark)"],
        "answer": "! (Exclamation mark)",
        "subject": "English"
    },
    {
        "question": "If you're drawing a cozy dog bed that's shaped like a perfect square, how many equal sides does a square have? 🐶",
        "options": ["Two", "Three", "Four", "Five"],
        "answer": "Four",
        "subject": "Maths"
    },
    {
        "question": "When your dog jumps up high to catch a bouncy ball, which natural force makes the ball (and your dog!) come back down to the ground? 💪",
        "options": ["Magnetism", "Friction", "Gravity", "Lift"],
        "answer": "Gravity",
        "subject": "Science"
    },
    {
        "question": "Long, long ago, in Ancient Egypt, people loved their dogs so much that they sometimes buried them with their owners! Which of these were the powerful rulers of Ancient Egypt? 👑",
        "options": ["Knights", "Vikings", "Pharaohs", "Cowboys"],
        "answer": "Pharaohs",
        "subject": "History"
    },
    {
        "question": "You're drawing a beautiful Golden Retriever puppy! Which colours would you mostly use for its soft, fluffy fur? 🎨",
        "options": ["Reds, purples, and blues", "Yellows, golds, and light browns", "Greys, blacks, and whites", "Bright pinks and greens"],
        "answer": "Yellows, golds, and light browns",
        "subject": "Art & Design"
    },
    {
        "question": "You're making a happy song about your dog! What is the super catchy part of a song that often repeats, and everyone can sing along to? 🎤",
        "options": ["The bridge", "The verse", "The chorus", "The outro"],
        "answer": "The chorus",
        "subject": "Music"
    },
    {
        "question": "Your tiny puppy, Pip, is so **adorable** when she sleeps in her basket. What does the word 'adorable' mean? ✨",
        "options": ["A bit grumpy", "Very cute and loveable", "Sleepy and quiet", "Big and noisy"],
        "answer": "Very cute and loveable",
        "subject": "English"
    },
    {
        "question": "Your dog's walking lead is 3 meters long. If you buy a new, longer lead that is 1.5 meters *longer* than the old one, how long is the new lead? 🎀",
        "options": ["1.5 meters", "3 meters", "4.5 meters", "5 meters"],
        "answer": "4.5 meters",
        "subject": "Maths"
    },
    {
        "question": "What very important thing do all living creatures, like your dog, need to drink every day to stay hydrated and healthy? 💧",
        "options": ["Milk", "Juice", "Water", "Fizzy pop"],
        "answer": "Water",
        "subject": "Science"
    },
    {
        "question": "Scientists believe that all of our cute, cuddly pet dogs today originally came from which wild animal, thousands of years ago? 🐺",
        "options": ["Bears", "Lions", "Wolves", "Cats"],
        "answer": "Wolves",
        "subject": "History"
    }
]

# --- Session State Initialization ---
if 'current_question_idx' not in st.session_state:
    st.session_state.current_question_idx = 0
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = [None] * len(quiz_questions)
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'quiz_finished' not in st.session_state:
    st.session_state.quiz_finished = False
if 'show_results' not in st.session_state:
    st.session_state.show_results = False
if 'bonus_challenge_answer' not in st.session_state:
    st.session_state.bonus_challenge_answer = ""

# --- Functions for Quiz Navigation ---
def next_question():
    if st.session_state.current_question_idx < len(quiz_questions) - 1:
        st.session_state.current_question_idx += 1
    else:
        st.session_state.quiz_finished = True
        st.session_state.show_results = True # Automatically show results when quiz finishes

def previous_question():
    if st.session_state.current_question_idx > 0:
        st.session_state.current_question_idx -= 1

def restart_quiz():
    st.session_state.current_question_idx = 0
    st.session_state.user_answers = [None] * len(quiz_questions)
    st.session_state.score = 0
    st.session_state.quiz_finished = False
    st.session_state.show_results = False
    st.session_state.bonus_challenge_answer = "" # Clear bonus challenge answer

def calculate_score():
    correct_answers_count = 0
    for i, q in enumerate(quiz_questions):
        if st.session_state.user_answers[i] == q["answer"]:
            correct_answers_count += 1
    st.session_state.score = correct_answers_count

# --- Streamlit App Layout ---

st.set_page_config(page_title="Cute Pups & Clever Minds Quiz!", page_icon="🐶")

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

st.markdown("<h1 class='main-header'>The Cute Pups & Clever Minds Quiz! 🐶✨</h1>", unsafe_allow_html=True)
st.markdown("Hi there, future dog trainer! Get ready to show off your super smarts with questions about school subjects, all inspired by our fluffy, four-legged friends! You are paw-some! 💖", unsafe_allow_html=True)

if not st.session_state.quiz_finished:
    current_q = quiz_questions[st.session_state.current_question_idx]

    st.markdown(f"<div class='question-box'>", unsafe_allow_html=True)
    st.markdown(f"<p class='subheader'>Question {st.session_state.current_question_idx + 1} of {len(quiz_questions)} - {current_q['subject']}</p>", unsafe_allow_html=True)
    
    # Use st.form to group question and options for better state management with radio buttons
    with st.form(key=f"question_form_{st.session_state.current_question_idx}"):
        st.markdown(f"**{current_q['question']}**")
        
        # Determine the initial index for the radio button
        current_answer_idx = 0
        if st.session_state.user_answers[st.session_state.current_question_idx] in current_q["options"]:
            current_answer_idx = current_q["options"].index(st.session_state.user_answers[st.session_state.current_question_idx])
            
        user_choice = st.radio(
            "Select your answer:",
            current_q["options"],
            index=current_answer_idx,
            key=f"q_{st.session_state.current_question_idx}_radio",
            horizontal=True # Display options horizontally for better readability
        )
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.session_state.current_question_idx > 0:
                st.form_submit_button("⬅️ Previous", on_click=previous_question)
        with col2:
            submitted = st.form_submit_button("Submit Answer & Next 🐾")

        if submitted:
            st.session_state.user_answers[st.session_state.current_question_idx] = user_choice
            calculate_score() # Update score after each submission
            next_question()
            st.rerun() # Rerun to display next question or results
    
    st.markdown(f"</div>", unsafe_allow_html=True)

else:
    st.markdown("<h2 class='main-header'>Quiz Complete! You're a top dog! 🎉</h2>", unsafe_allow_html=True)
    st.markdown(f"<div class='score-display'>Your final score: {st.session_state.score} out of {len(quiz_questions)}!</div>", unsafe_allow_html=True)

    st.write("---")
    st.markdown("### Review Your Answers:")
    for i, q in enumerate(quiz_questions):
        st.markdown(f"**Question {i+1}:** {q['question']}")
        user_ans = st.session_state.user_answers[i]
        correct_ans = q['answer']

        if user_ans == correct_ans:
            st.markdown(f"<p class='feedback-correct'>✅ Your Answer: {user_ans}</p>", unsafe_allow_html=True)
        else:
            st.markdown(f"<p class='feedback-incorrect'>❌ Your Answer: {user_ans if user_ans else 'Not answered'}</p>", unsafe_allow_html=True)
            st.markdown(f"<p class='feedback-correct'>Correct Answer: {correct_ans}</p>", unsafe_allow_html=True)
        st.write("") # Add a little space

    st.markdown("---")
    st.markdown("### Bonus Challenge (Just for fun!)")
    st.write("If you could design the most amazing, super-fun dog park in the world, what exciting things would it have for all the cute pups?")
    st.session_state.bonus_challenge_answer = st.text_area("Your amazing idea:", value=st.session_state.bonus_challenge_answer, key="bonus_challenge_text_area")

    st.button("Start Again! 🐕", on_click=restart_quiz)
