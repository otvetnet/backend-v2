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
    
    # Calculate total for games 1-5
    games_1_5_total = sum(group_scores.get(i, 0) for i in range(1, 6))
    # Calculate total for all games (1-6)
    games_total = games_1_5_total + group_scores.get(6, 0)
    
    # Add totals to g_fields
    g_fields["games_1_5_total"] = games_1_5_total
    g_fields["games_total"] = games_total

    # 6. Определение выбранной группы (для обычного прохождения)
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

    # 7. Поиск существующей записи
    existing_response = None
    if user_uuid:
        existing_response = session.exec(
            select(SurveyResponse).where(
                SurveyResponse.survey_id == submission.survey_id,
                SurveyResponse.user_id == user_uuid
            )
        ).first()

    # 8. Определяем, это рефлексия или нет
    is_reflection = getattr(submission, "is_reflection", False)
    if not is_reflection and existing_response is not None and len(submission.answers) <= 5:
        # fallback для старых клиентов без флага
        is_reflection = True

    # 9. РАСЧЕТ ПОЛЕЙ РЕФЛЕКСИИ - ВАЖНО: зависит от типа прохождения
    dep_answers = []
    dep_fields = {f"dep{i}": 0 for i in range(1, 6)}
    dep_total = 0

    print(f"[DEBUG] is_reflection: {is_reflection}")
    print(f"[DEBUG] submission answers: {[(a.question_id, a.answer_option_id) for a in submission.answers]}")
    print(f"[DEBUG] group_answers: {group_answers}")

    if is_reflection and existing_response:
        # При рефлексии берем ответы из текущих group_answers
        current_group = None
        # Находим группу по первому ответу в group_answers
        for gid, answers in group_answers.items():
            if answers:  # если есть ответы в этой группе
                current_group = gid
                break
        
        if current_group and 1 <= current_group <= 6:
            # Берем первые 5 ответов этой группы в порядке ID вопросов
            sorted_answers = sorted(group_answers[current_group], key=lambda x: x[0])
            dep_answers = [v for (_qid, v) in sorted_answers][:5]
            print(f"[DEBUG] Taking first 5 answers from group {current_group}: {dep_answers}")
    else:
        # При обычном прохождении используем вычисленный chosen_group
        if chosen_group and group_answers.get(chosen_group):
            sorted_by_qid = sorted(group_answers[chosen_group], key=lambda x: x[0])
            dep_answers = [v for (_qid, v) in sorted_by_qid][:5]

    # Заполняем dep_fields на основе dep_answers
    dep_fields = {f"dep{i}": (dep_answers[i-1] if i-1 < len(dep_answers) else 0) for i in range(1, 6)}
    dep_total = sum(dep_answers)

    print(f"[DEBUG] Final dep_fields: {dep_fields}, dep_total: {dep_total}")

    # 10. Создание или обновление записи
    if existing_response:
        if is_reflection:
            # --- РЕФЛЕКСИЯ: обновляем только поля dep1-dep5 и dep_total ---
            print("[INFO] Reflection mode detected — updating only reflection fields")
            
            # Обновляем поля рефлексии новыми значениями
            existing_response.dep1 = dep_fields["dep1"]
            existing_response.dep2 = dep_fields["dep2"]
            existing_response.dep3 = dep_fields["dep3"]
            existing_response.dep4 = dep_fields["dep4"]
            existing_response.dep5 = dep_fields["dep5"]
            existing_response.dep_total = dep_total
            
            print(f"[DEBUG] Reflection updated: dep1={dep_fields['dep1']}, dep2={dep_fields['dep2']}, "
                  f"dep3={dep_fields['dep3']}, dep4={dep_fields['dep4']}, dep5={dep_fields['dep5']}, "
                  f"dep_total={dep_total}")
                  
        else:
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
            
            # При обычном прохождении обновляем ВСЕ поля, включая dep_id
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

    # 11. Выбор игры 
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