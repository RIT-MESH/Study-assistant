import os
import streamlit as st
from dotenv import load_dotenv
from src.utils.helpers import *
from src.generator.question_generator import QuestionGenerator

load_dotenv()

def main():
    st.set_page_config(page_title="JLPT N1-N2 Practice Quiz", page_icon="📝")

    if 'quiz_manager' not in st.session_state:
        st.session_state.quiz_manager = QuizManager()

    if 'quiz_generated' not in st.session_state:
        st.session_state.quiz_generated = False

    if 'quiz_submitted' not in st.session_state:
        st.session_state.quiz_submitted = False

    if 'rerun_trigger' not in st.session_state:
        st.session_state.rerun_trigger = False
        
    st.title("JLPT N1-N2 Practice Quiz Generator")

    st.sidebar.header("Quiz Settings")

    # Changed the topic input to a level selector for JLPT
    level = st.sidebar.selectbox(
        "Select JLPT Level",
        ["N1", "N2"],
        index=0
    )

    # Changed question type to be specific to JLPT sections
    question_type = st.sidebar.selectbox(
        "Select Question Type",
        ["Grammar (文法)", "Vocabulary (語彙)", "Reading (読解)"],
        index=0
    )

    # Re-purposed difficulty to be part of the topic string
    difficulty_mapping = {"Grammar (文法)": "Grammar", "Vocabulary (語彙)": "Vocabulary", "Reading (読解)": "Reading Comprehension"}
    topic = f"JLPT {level} {difficulty_mapping[question_type]}"

    num_questions = st.sidebar.number_input(
        "Number of Questions",
        min_value=1, max_value=10, value=5
    )
    
    if st.sidebar.button("Generate Quiz"):
        st.session_state.quiz_submitted = False

        generator = QuestionGenerator()
        # The 'difficulty' parameter is now implicitly handled by the detailed topic string
        success = st.session_state.quiz_manager.generate_questions(
            generator,
            topic, "Multiple Choice", "Hard", num_questions
        )

        st.session_state.quiz_generated = success
        rerun()

    if st.session_state.quiz_generated and st.session_state.quiz_manager.questions:
        st.header(f"JLPT {level} - {question_type} Quiz")
        st.session_state.quiz_manager.attempt_quiz()

        if st.button("Submit Quiz"):
            st.session_state.quiz_manager.evaluate_quiz()
            st.session_state.quiz_submitted = True
            rerun()

    if st.session_state.quiz_submitted:
        st.header("Quiz Results")
        results_df = st.session_state.quiz_manager.generate_result_dataframe()

        if not results_df.empty:
            correct_count = results_df["is_correct"].sum()
            total_questions = len(results_df)
            score_percentage = (correct_count / total_questions) * 100
            st.write(f"**Your Score: {score_percentage:.2f}%** ({correct_count} out of {total_questions} correct)")
            st.markdown("---")

            for _, result in results_df.iterrows():
                question_num = result['question_number']
                if result['is_correct']:
                    st.success(f"✅ **Question {question_num}:** {result['question']}")
                else:
                    st.error(f"❌ **Question {question_num}:** {result['question']}")
                    st.write(f"**Your answer:** {result['user_answer']}")
                    st.write(f"**Correct answer:** {result['correct_answer']}")
                
                st.markdown("-------")

            if st.button("Save Results"):
                saved_file = st.session_state.quiz_manager.save_to_csv()
                if saved_file:
                    with open(saved_file, 'rb') as f:
                        st.download_button(
                            label="Download Results",
                            data=f.read(),
                            file_name=os.path.basename(saved_file),
                            mime='text/csv'
                        )
                else:
                    st.warning("No results available to save.")

if __name__ == "__main__":
    main()

    