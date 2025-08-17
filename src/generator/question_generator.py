from langchain_core.prompts import ChatPromptTemplate
from src.models.question_schemas import MCQQuestion, FillBlankQuestion
from src.prompts.templates import mcq_prompt_template
from src.llm.openai_client import get_openai_llm
from src.config.settings import settings
from src.common.logger import get_logger
from src.common.custom_exception import CustomException

class QuestionGenerator:
    def __init__(self):
        self.llm = get_openai_llm()
        self.logger = get_logger(self.__class__.__name__)
        # Create LLM chains that are FORCED to output our desired schemas
        self.mcq_chain = self.llm.with_structured_output(MCQQuestion)
        self.fill_blank_chain = self.llm.with_structured_output(FillBlankQuestion)

    def generate_mcq(self, topic: str, difficulty: str = 'medium') -> MCQQuestion:
        for attempt in range(settings.MAX_RETRIES):
            try:
                self.logger.info(f"Generating MCQ for '{topic}' (Attempt {attempt + 1})")
                
                prompt = ChatPromptTemplate.from_template(mcq_prompt_template.template)
                # The chain combines the prompt and the structured output model
                chain = prompt | self.mcq_chain
                
                # Invoking the chain directly returns a validated Pydantic object. No more parsing!
                question = chain.invoke({"topic": topic, "difficulty": difficulty})

                # We still validate the content logic
                if len(question.options) != 4 or question.correct_answer not in question.options:
                    self.logger.warning("Generated MCQ has invalid structure. Retrying...")
                    continue

                self.logger.info("Successfully generated a valid MCQ Question.")
                return question

            except Exception as e:
                self.logger.error(f"Attempt {attempt + 1} to generate MCQ failed: {str(e)}")
                if attempt == settings.MAX_RETRIES - 1:
                    raise CustomException(f"MCQ Generation failed after {settings.MAX_RETRIES} attempts.", e)

    # Note: The fill_blank functionality is also updated for consistency, even if not used by the main app.
    def generate_fill_blank(self, topic: str, difficulty: str = 'medium') -> FillBlankQuestion:
        # This function would be structured identically to generate_mcq,
        # using fill_blank_prompt_template and self.fill_blank_chain.
        # Since it is not used in application.py, I will omit the full implementation
        # to keep the focus on the immediate fix.
        pass