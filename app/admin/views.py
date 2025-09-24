from starlette_admin.contrib.sqlmodel import ModelView

from starlette_admin.fields import StringField, IntegerField, JSONField, HasMany
from app.admin.fields import UserFullNameField, CityNameField
from app.models.game import Game, Scene, Certificate
from app.models.survey import AnswerOption, Question, Survey, SurveyResponse
from app.models.user import User


class SurveyView(ModelView):
    model = Survey
    name = 'Опрос'
    label = 'Формы'
    fields = [
        "id",
        "title",
        "questions",
    ]

class QuestionView(ModelView):
    model = Question
    name = 'Вопрос'
    label = 'Вопросы'

    fields = [
        "id",
        "text",
        "survey",
        "options"

    ]

class AnswerOptionView(ModelView):
    model = AnswerOption
    name = 'Ответ'
    label = 'Ответы'
    fields = [
        "id",
        "text",
        "order",
        'question'
    ]


class SurveyResponseView(ModelView):
    model = SurveyResponse
    name = "Результат"
    label = "Результаты"

    fields = [
        "id",
        IntegerField("score", label="Балл"),
        UserFullNameField(name="ФИО"),
    ]


class UserView(ModelView):
    model = User
    name = 'Аккаунт'
    label = "Аккаунты"

    fields = [
        "id",
        StringField("last_name", label="Фамилия"),
        StringField("first_name", label="Имя"),
        StringField("middle_name", label="Отчество"),
        IntegerField("age", label="Возраст"),
        StringField("school", label="Школа"),
        CityNameField(name="Город"),
    ]


class GameView(ModelView):
    model = Game
    name = 'Игра'
    label = 'Игры'

    fields = [
        "id",
        "title",
        "description",
        "duration",
        "cover_image",
        "music",
    ]


class SceneView(ModelView):
    model = Scene
    name = 'Сцена'
    label = 'Сцены'

    fields = [
        "id",
        IntegerField("game_id", label="игра"),
        "type",
        "order",
        JSONField("payload", label="payload"),
    ]


class CertificateView(ModelView):
    model = Certificate
    name = 'Сертификат'
    label = 'Сертификаты'
    fields = [
        "id"
    ]