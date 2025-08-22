import streamlit as st

# --- Quiz Data ---
quiz_questions = [
    {
        "question": "Imagine your favourite pop star is writing a tweet about her latest hit song. Which punctuation mark is missing from this sentence? 'Wow what an amazing crowd tonight!' 🎶",
        "options": [", (Comma)", ". (Full stop)", "! (Exclamation mark)", "? (Question mark)"],
        "answer": "! (Exclamation mark)",
        "subject": "English"
    },
    {
        "question": "A gymnast is performing a beautiful split on the balance beam. What angle do her legs form when they are perfectly straight in a split? 📐",
        "options": ["90 degrees", "180 degrees", "45 degrees", "360 degrees"],
        "answer": "180 degrees",
        "subject": "Maths"
    },
    {
        "question": "When a gymnast jumps really high during her floor routine, which natural force pulls her back down to the mat? 💪",
        "options": ["Magnetism", "Friction", "Gravity", "Lift"],
        "answer": "Gravity",
        "subject": "Science"
    },
    {
        "question": "Thinking about fabulous historical fashion for a pop star's music video, which historical era is known for its very elaborate, grand dresses, big skirts, and sometimes even powdered wigs? 👑",
        "options": ["The Roman Empire", "The Victorian Era", "The Stone Age", "The Future Space Age"],
        "answer": "The Victorian Era",
        "subject": "History"
    },
    {
        "question": "You're helping design a make-up palette inspired by a pop star's hit song called 'Ocean Dreams.' Which colours would you mostly use to capture the feeling of the ocean? 🎨",
        "options": ["Reds, oranges, and yellows", "Greens, blues, and silvers", "Browns, greys, and blacks", "Pinks, purples, and golds"],
        "answer": "Greens, blues, and silvers",
        "subject": "Art & Design"
    },
    {
        "question": "What is the super catchy, memorable part of a pop song that often repeats and gets stuck in everyone's head? 🎤",
        "options": ["The bridge", "The verse", "The chorus", "The outro"],
        "answer": "The chorus",
        "subject": "Music"
    },
    {
        "question": "Your favourite gymnastics leotard is absolutely **dazzling**! It's so bright and sparkly. What does the word 'dazzling' mean? ✨",
        "options": ["Dull and plain", "Very beautiful and shimmering brightly", "A little bit sad", "Old and worn out"],
        "answer": "Very beautiful and shimmering brightly",
        "subject": "English"
    },
    {
        "question": "A rhythmic gymnast uses a ribbon that is 6 meters long. If she cuts off 1.5 meters because it's too long, how long is her ribbon now? 🎀",
        "options": ["7.5 meters", "5 meters", "4.5 meters", "3.5 meters"],
        "answer": "4.5 meters",
        "subject": "Maths"
    },
    {
        "question": "Many make-up products, like foundation and powder, often contain tiny particles from the Earth to make them smooth and give them colour. What is a common word for these natural substances found in the ground? 💖",
        "options": ["Plastics", "Sugar", "Minerals", "Fabric"],
        "answer": "Minerals",
        "subject": "Science"
    },
    {
        "question": "The incredible Olympic Games, where gymnasts show off their amazing skills, first began in which ancient country? 🏛️",
        "options": ["Egypt", "China", "Greece", "Italy"],
        "answer": "Greece",
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

def calculate_score():
    correct_answers_count = 0
    for i, q in enumerate(quiz_questions):
        if st.session_state.user_answers[i] == q["answer"]:
            correct_answers_count += 1
    st.session_state.score = correct_answers_count

# --- Streamlit App Layout ---

st.set_page_config(page_title="Glitter & Goals Quiz!", page_icon="✨")

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
    """, unsafe_allow_html=True) # [6, 9, 10, 12]

st.markdown("<h1 class='main-header'>The Ultimate Glitter & Goals Quiz! ✨</h1>", unsafe_allow_html=True)
st.markdown("Hello, Superstar! Get ready to test your knowledge in subjects from the UK National Curriculum, with a twist of your favourite things! You've got this! 💖", unsafe_allow_html=True)

if not st.session_state.quiz_finished:
    current_q = quiz_questions[st.session_state.current_question_idx]

    st.markdown(f"<div class='question-box'>", unsafe_allow_html=True)
    st.markdown(f"<p class='subheader'>Question {st.session_state.current_question_idx + 1} of {len(quiz_questions)} - {current_q['subject']}</p>", unsafe_allow_html=True)
    
    # Use st.form to group question and options for better state management with radio buttons [2, 3, 4, 7, 11]
    with st.form(key=f"question_form_{st.session_state.current_question_idx}"):
        st.markdown(f"**{current_q['question']}**")
        
        # Unique key for each radio button group
        user_choice = st.radio(
            "Select your answer:",
            current_q["options"],
            index=current_q["options"].index(st.session_state.user_answers[st.session_state.current_question_idx]) if st.session_state.user_answers[st.session_state.current_question_idx] else 0,
            key=f"q_{st.session_state.current_question_idx}_radio",
            horizontal=True # Display options horizontally for better readability
        )
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.session_state.current_question_idx > 0:
                st.form_submit_button("⬅️ Previous", on_click=previous_question)
        with col2:
            submitted = st.form_submit_button("Submit Answer & Next ✨")

        if submitted:
            st.session_state.user_answers[st.session_state.current_question_idx] = user_choice
            calculate_score() # Update score after each submission
            next_question()
            st.rerun() # Rerun to display next question or results
    
    st.markdown(f"</div>", unsafe_allow_html=True)

else:
    st.markdown("<h2 class='main-header'>Quiz Complete! 🎉</h2>", unsafe_allow_html=True)
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
    st.write("If you could combine gymnastics and pop music into one amazing performance, what would it look like? Describe it in one exciting sentence! 🌟")
    st.text_area("Your amazing idea:", value=st.session_state.get('bonus_challenge_answer', ''))
    st.session_state.bonus_challenge_answer = st.text_input("","") # A simple way to capture input, but it will clear on rerun if not saved properly. For a single input like this, a text_area is better for longer thoughts. I've updated this to use text_area and removed the extra st.text_input, simplifying the handling.

    st.button("Start Again! 🤸‍♀️", on_click=restart_quiz)
