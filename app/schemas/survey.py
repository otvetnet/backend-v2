from typing import List
from pydantic import BaseModel
from sqlmodel import SQLModel
from app.models.survey import AnswerOptionBase, QuestionBase, SurveyBase


class AnswerOptionPublic(AnswerOptionBase):
    id: int
    text: str
    order: int

class QuestionPublic(QuestionBase):
    id: int
    text: str
    options: List[AnswerOptionPublic]


class SurveyPublic(SurveyBase):
    id: int
    title: str
    questions: List[QuestionPublic]


class SurveysPublic(SQLModel):
    surveys: List[SurveyPublic]


class AnswerSubmission(BaseModel):
    question_id: int
    answer_option_id: int


class SurveySubmission(BaseModel):
    survey_id: int
    user_id: str
    answers: List[AnswerSubmission]


class SurveyResultPublic(BaseModel):
    survey_id: int
    score: int
    suggested_game: int