import uuid
from typing import List, TYPE_CHECKING, Optional
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    # import for type checking / linters only to avoid circular import at runtime
    from app.models.user import User

class SurveyBase(SQLModel):
    title: str


class Survey(SurveyBase, table=True):
    id: int = Field(default=None, primary_key=True)
    questions: List["Question"] = Relationship(back_populates="survey")
    responses: List["SurveyResponse"] = Relationship(back_populates="survey")

class QuestionBase(SQLModel):
    text: str
    # group identifier for selection algorithm (e.g., 1..5)
    group_id: int = Field(default=0)
    # URL or path to voice file for this question
    voice: str | None = Field(default=None)


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
    
    # Personal data fields
    first_name: str = Field(default="")
    last_name: str = Field(default="")
    middle_name: str = Field(default="")
    age: int = Field(default=0)
    school: str = Field(default="")
    city: str = Field(default="")
    #score: int = Field(default=0.0)
    q1: int = Field(default=0)
    q2: int = Field(default=0)
    q3: int = Field(default=0)
    q4: int = Field(default=0)
    q5: int = Field(default=0)
    g1_total: int = Field(default=0)
    q6: int = Field(default=0)
    q7: int = Field(default=0)
    q8: int = Field(default=0)
    q9: int = Field(default=0)
    q10: int = Field(default=0)
    g2_total: int = Field(default=0)
    q11: int = Field(default=0)
    q12: int = Field(default=0)
    q13: int = Field(default=0)
    q14: int = Field(default=0)
    q15: int = Field(default=0)
    g3_total: int = Field(default=0)
    q16: int = Field(default=0)
    q17: int = Field(default=0)
    q18: int = Field(default=0)
    q19: int = Field(default=0)
    q20: int = Field(default=0)
    g4_total: int = Field(default=0)
    q21: int = Field(default=0)
    q22: int = Field(default=0)
    q23: int = Field(default=0)
    q24: int = Field(default=0)
    q25: int = Field(default=0)
    g5_total: int = Field(default=0)
    q26: int = Field(default=0)
    q27: int = Field(default=0)
    q28: int = Field(default=0)
    q29: int = Field(default=0)
    q30: int = Field(default=0)
    g6_total: int = Field(default=0)

    dep_id: int = Field(default=0)
    # dependency (зависимость) 1..5 and total
    dep1: int = Field(default=0)
    dep2: int = Field(default=0)
    dep3: int = Field(default=0)
    dep4: int = Field(default=0)
    dep5: int = Field(default=0)
    dep_total: int = Field(default=0)

    # datetime when the survey was submitted (for statistics)
    finished_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    user: "User" = Relationship(back_populates="responses")
    survey: "Survey" = Relationship(back_populates="responses")