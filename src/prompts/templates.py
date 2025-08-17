from langchain.prompts import PromptTemplate

# This prompt now focuses ONLY on the desired content, not the format.
mcq_prompt_template = PromptTemplate(
    template=(
        "Generate a multiple-choice question about the topic: {topic} "
        "at a {difficulty} difficulty level.\n"
        "The question and options must be in Japanese and should focus on "
        "JLPT N1 or N2 level grammar points."
    ),
    input_variables=["topic", "difficulty"]
)

# This prompt is also simplified.
fill_blank_prompt_template = PromptTemplate(
    template=(
        "Generate a fill-in-the-blank question about the topic: {topic} "
        "at a {difficulty} difficulty level.\n"
        "The question must be in Japanese, contain a blank represented by '_____', "
        "and should focus on JLPT N1 or N2 level grammar points."
    ),
    input_variables=["topic", "difficulty"]
)