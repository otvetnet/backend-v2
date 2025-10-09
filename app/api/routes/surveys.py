from typing import Any
from fastapi import APIRouter
from sqlalchemy.orm import selectinload
from sqlmodel import select, func
from app.api.deps import SessionDep
from app.models.survey import Survey, Question, SurveyResponse, AnswerOption
from app.schemas.survey import SurveysPublic, SurveySubmission, SurveyResultPublic

router = APIRouter(
    prefix="/surveys",
    tags=["surveys"]
)


@router.get("/", response_model=SurveysPublic)
def get_surveys(*, session: SessionDep) -> Any:
    """
    Get all surveys
    """
    surveys = session.exec(
        select(Survey).options(
            selectinload(Survey.questions)
                .selectinload(Question.options)
        )
    ).all()

    return SurveysPublic(surveys=surveys)

@router.post("/submit", response_model=SurveyResultPublic)
def submit(*, session: SessionDep, submission: SurveySubmission) -> Any:
    options_ids = [a.answer_option_id for a in submission.answers]
    options = session.exec(
        select(AnswerOption).where(AnswerOption.id.in_(options_ids))
    ).all()

    score = sum(opt.order for opt in options)

    survey_response = SurveyResponse(
        survey_id=submission.survey_id,
        user_id=submission.user_id,
        score=score,
    )

    session.add(survey_response)
    session.commit()
    session.refresh(survey_response)

    return SurveyResultPublic(
        survey_id=survey_response.survey_id,
        score=survey_response.score,
        suggested_game=1
    )