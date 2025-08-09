from typing import List  # optional; you can use list[str] instead
from pydantic import BaseModel, Field, field_validator, model_validator

class MCQQuestion(BaseModel):
    question: str = Field(description="The question text")
    options: List[str] = Field(description="List of 4 options")  # or list[str]
    correct_answer: str = Field(description="The correct answer from the options")

    @field_validator('question', mode='before')
    def clean_question(cls, v):
        if isinstance(v, dict):
            return v.get('description', str(v))
        return str(v)

    @field_validator('options')
    def check_options_len(cls, v):
        if len(v) != 4:
            raise ValueError("options must contain exactly 4 items")
        return [str(x) for x in v]

    @model_validator(mode='after')
    def ensure_answer_in_options(self):
        if self.correct_answer not in self.options:
            raise ValueError("correct_answer must be one of the options")
        return self


class FillBlankQuestion(BaseModel):
    question: str = Field(description="The question text with '___' for the blank")
    answer: str = Field(description="The correct word or phrase for the blank")

    @field_validator('question', mode='before')
    def clean_question(cls, v):
        if isinstance(v, dict):
            return v.get('description', str(v))
        return str(v)
