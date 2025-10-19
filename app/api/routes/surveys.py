from typing import Any, Dict
from fastapi import APIRouter
from sqlalchemy.orm import selectinload
from sqlmodel import select, func
from app.api.deps import SessionDep
from app.models.survey import Survey, Question, SurveyResponse, AnswerOption
from app.models.game import Game
from app.schemas.survey import SurveysPublic, SurveySubmission, SurveyResultPublic
from app.models.user import User
import uuid as _uuid

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
    # 1. Загрузка и маппинг ответов и вопросов
    options_ids = [a.answer_option_id for a in submission.answers]
    options = session.exec(
        select(AnswerOption).where(AnswerOption.id.in_(options_ids))
    ).all()
    opt_by_id = {opt.id: opt for opt in options}

    question_ids = [a.question_id for a in submission.answers]
    questions = session.exec(
        select(Question).where(Question.id.in_(question_ids))
    ).all()
    questions_by_id = {q.id: q for q in questions}

    # 2. Подготовка контейнеров для подсчёта
    answer_map: Dict[int, int] = {}  # question_id -> answer (0/1)
    group_scores: Dict[int, int] = {}  # group_id -> total score
    group_answers = {i: [] for i in range(1, 7)}  # group_id -> [(question_id, answer)]
    total_score = 0

    # 3. Обработка ответов
    for ans in submission.answers:
        q = questions_by_id.get(ans.question_id)
        if not q:
            continue
        opt = opt_by_id.get(ans.answer_option_id)
        val = 1 if (opt is not None and getattr(opt, "order", 0) == 1) else 0
        answer_map[q.id] = val
        total_score += val
        grp = getattr(q, "group_id", 0) or 0
        group_scores[grp] = group_scores.get(grp, 0) + val
        if 1 <= grp <= 6:
            group_answers[grp].append((q.id, val))

    # 4. Получение личных данных из User
    user_data = {
        "first_name": "",
        "middle_name": "",
        "last_name": "",
        "age": 0,
        "school": "",
        "city": ""
    }
    user_uuid = None

    try:
        if submission.user_id:
            user_uuid = _uuid.UUID(str(submission.user_id))
            user = session.get(User, user_uuid)
            if user:
                if user.first_name:
                    user_data["first_name"] = user.first_name
                if user.middle_name:
                    user_data["middle_name"] = user.middle_name
                if user.last_name:
                    user_data["last_name"] = user.last_name
                if user.age and user.age > 0:
                    user_data["age"] = user.age
                if user.school:
                    user_data["school"] = user.school
                if user.city and user.city.name:
                    user_data["city"] = user.city.name
    except Exception as e:
        print(f"Error getting user data: {e}")

    # 5. Подготовка полей для БД
    q_fields = {f"q{i}": answer_map.get(i, 0) for i in range(1, 31)}
    g_fields = {f"g{i}_total": group_scores.get(i, 0) for i in range(1, 7)}

    # 6. Определение выбранной группы
    filtered_scores = {g: s for g, s in group_scores.items() if g and g > 0}
    chosen_group = 0
    if filtered_scores:
        max_score = max(filtered_scores.values())
        candidate_groups = [g for g, s in filtered_scores.items() if s == max_score]
        chosen_group = min(candidate_groups)
    else:
        group_ids_in_answers = set()
        for ans in submission.answers:
            q = questions_by_id.get(ans.question_id)
            if q and q.group_id:
                group_ids_in_answers.add(q.group_id)
        if len(group_ids_in_answers) == 1:
            chosen_group = list(group_ids_in_answers)[0]

    # 7. Поля рефлексии (dep1..dep5)
    dep_answers = []
    if chosen_group and group_answers.get(chosen_group):
        sorted_by_qid = sorted(group_answers[chosen_group], key=lambda x: x[0])
        dep_answers = [v for (_qid, v) in sorted_by_qid][:5]

    dep_fields = {f"dep{i}": (dep_answers[i-1] if i-1 < len(dep_answers) else 0) for i in range(1, 6)}
    dep_total = sum(dep_answers)

    # 8. Поиск существующей записи
    existing_response = None
    if user_uuid:
        existing_response = session.exec(
            select(SurveyResponse).where(
                SurveyResponse.survey_id == submission.survey_id,
                SurveyResponse.user_id == user_uuid
            )
        ).first()

    # 9. Определяем, это рефлексия или нет
    # Лучше использовать явный флаг из схемы (submission.is_reflection)
    is_reflection = getattr(submission, "is_reflection", False)
    if not is_reflection and existing_response is not None and len(submission.answers) <= 5:
        # fallback для старых клиентов без флага
        is_reflection = True

    # 10. Создание или обновление записи
    if existing_response:
        if not is_reflection:
            # --- обычное прохождение ---
            answered_qids = set([ans.question_id for ans in submission.answers])
            for k, v in q_fields.items():
                try:
                    qid = int(k[1:])
                except Exception:
                    continue
                if qid in answered_qids:
                    setattr(existing_response, k, v)

            affected_groups = set()
            for ans in submission.answers:
                q = questions_by_id.get(ans.question_id)
                if q and q.group_id:
                    affected_groups.add(q.group_id)
            for k, v in g_fields.items():
                try:
                    gid = int(k[1])
                except Exception:
                    continue
                if gid in affected_groups:
                    setattr(existing_response, k, v)

            # Обновляем личные данные
            existing_response.first_name = user_data["first_name"]
            existing_response.middle_name = user_data["middle_name"]
            existing_response.last_name = user_data["last_name"]
            existing_response.age = user_data["age"]
            existing_response.school = user_data["school"]
            existing_response.city = user_data["city"]
        else:
            print("[INFO] Reflection mode detected — updating only dep fields")

        # --- обновляем dep поля (всегда) ---
        existing_response.dep1 = dep_fields["dep1"]
        existing_response.dep2 = dep_fields["dep2"]
        existing_response.dep3 = dep_fields["dep3"]
        existing_response.dep4 = dep_fields["dep4"]
        existing_response.dep5 = dep_fields["dep5"]
        existing_response.dep_total = dep_total
        existing_response.dep_id = chosen_group

        survey_response = existing_response
    else:
        # --- первая запись ---
        survey_response = SurveyResponse(
            survey_id=submission.survey_id,
            user_id=user_uuid,
            first_name=user_data["first_name"],
            middle_name=user_data["middle_name"],
            last_name=user_data["last_name"],
            age=user_data["age"],
            school=user_data["school"],
            city=user_data["city"],
            dep_id=chosen_group,
            **q_fields,
            **g_fields,
            dep1=dep_fields["dep1"],
            dep2=dep_fields["dep2"],
            dep3=dep_fields["dep3"],
            dep4=dep_fields["dep4"],
            dep5=dep_fields["dep5"],
            dep_total=dep_total
        )

    session.add(survey_response)
    session.commit()
    session.refresh(survey_response)

    # 11. Выбор игры (оригинальный механизм)
    suggested_game_id: int | None = None
    if chosen_group:
        game = session.exec(
            select(Game).where(Game.game_group_id == chosen_group).order_by(Game.id)
        ).first()
        if game:
            suggested_game_id = game.id

    return SurveyResultPublic(
        survey_id=survey_response.survey_id,
        score=total_score,
        suggested_game=suggested_game_id,
    )
