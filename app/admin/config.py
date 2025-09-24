from starlette_admin.contrib.sqlmodel import ModelView, Admin
from starlette_admin import DropDown

from app.admin.auth import AdminAuth
from app.admin.views import SurveyView, QuestionView, AnswerOptionView, SurveyResponseView, UserView, GameView, \
    SceneView, CertificateView
from app.core.database import engine
from app.models.game import Game, Scene, Certificate
from app.models.survey import Survey, Question, AnswerOption, SurveyResponse
from app.models.user import User


admin = Admin(
    title="Ответ НЕТ. CMS",
    base_url="/admin",
    logo_url=None,
    auth_provider=AdminAuth(),
    engine=engine
)

admin.add_view(
    DropDown(
        "Пользователи",
        icon="fas fa-users",
        views=[
            UserView(User),
            CertificateView(Certificate)
        ]
    )
)

admin.add_view(
    DropDown(
        "Опросы",
        icon="fas fa-poll",
        views=[
            SurveyView(Survey),
            QuestionView(Question),
            AnswerOptionView(AnswerOption),
            SurveyResponseView(SurveyResponse),
        ]
    )
)

admin.add_view(
    DropDown(
        "Конструктор",
        icon="fas fa-magic",
        views=[
            GameView(Game),
            SceneView(Scene),
        ]
    )
)