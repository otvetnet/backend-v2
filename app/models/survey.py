import uuid
from typing import List
from sqlmodel import Field, SQLModel, Relationship

class SurveyBase(SQLModel):
    title: str


class Survey(SurveyBase, table=True):
    id: int = Field(default=None, primary_key=True)
    questions: List["Question"] = Relationship(back_populates="survey")
    responses: List["SurveyResponse"] = Relationship(back_populates="survey")

class QuestionBase(SQLModel):
    text: str


class Question(QuestionBase, table=True):
    id: int = Field(default=None, primary_key=True)
    survey_id: int = Field(default=None, foreign_key="survey.id")
    survey: "Survey" = Relationship(back_populates="questions")
    options: List["AnswerOption"] = Relationship(back_populates="question")


class AnswerOptionBase(SQLModel):
    text: str
    order: int


class AnswerOption(AnswerOptionBase, table=True):
    id: int = Field(default=None, primary_key=True)
    question_id: int = Field(default=None, foreign_key="question.id")
    question: "Question" = Relationship(back_populates="options")


class SurveyResponse(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    survey_id: int = Field(default=None, foreign_key="survey.id")
    user_id: uuid.UUID = Field(default=None, foreign_key="user.id")
    score: int = Field(default=0.0)

    user: "User" = Relationship(back_populates="responses")
    survey: "Survey" = Relationship(back_populates="responses")