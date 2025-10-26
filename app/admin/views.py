from starlette_admin.contrib.sqlmodel import ModelView

from starlette_admin.fields import StringField, IntegerField, JSONField, HasMany
from app.admin.fields import UserFullNameField, CityNameField, DateField
from app.models.game import Game, Scene, Certificate, GameResult
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
        IntegerField("group_id", label="group_id"),
        "text",
        StringField("voice", label="Озвучка"),
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
        StringField("last_name", label="Фамилия"),
        StringField("first_name", label="Имя"),
        IntegerField("age", label="Возраст"),
        StringField("city", label="Город"),
        StringField("school", label="Школа"),
        DateField(name="finished_at", label="Дата прохождения"),
        IntegerField("q1", label="1.1"),
        IntegerField("q2", label="1.2"),
        IntegerField("q3", label="1.3"),
        IntegerField("q4", label="1.4"),
        IntegerField("q5", label="1.5"),
        IntegerField("g1_total", label="Итого 1"),
        IntegerField("q6", label="2.1"),
        IntegerField("q7", label="2.2"),
        IntegerField("q8", label="2.3"),
        IntegerField("q9", label="2.4"),
        IntegerField("q10", label="2.5"),
        IntegerField("g2_total", label="Итого 2"),
        IntegerField("q11", label="3.1"),
        IntegerField("q12", label="3.2"),
        IntegerField("q13", label="3.3"),
        IntegerField("q14", label="3.4"),
        IntegerField("q15", label="3.5"),
        IntegerField("g3_total", label="Итого 3"),
        IntegerField("q16", label="4.1"),
        IntegerField("q17", label="4.2"),
        IntegerField("q18", label="4.3"),
        IntegerField("q19", label="4.4"),
        IntegerField("q20", label="4.5"),
        IntegerField("g4_total", label="Итого 4"),
        IntegerField("q21", label="5.1"),
        IntegerField("q22", label="5.2"),
        IntegerField("q23", label="5.3"),
        IntegerField("q24", label="5.4"),
        IntegerField("q25", label="5.5"),
        IntegerField("g5_total", label="Итого 5"),
        IntegerField("q26", label="6.1"),
        IntegerField("q27", label="6.2"),
        IntegerField("q28", label="6.3"),
        IntegerField("q29", label="6.4"),
        IntegerField("q30", label="6.5"),
        IntegerField("g6_total", label="Итого 6"),
        IntegerField("dep_id", label="Номер зависимости"),
        IntegerField("dep1", label="Рефлексия 1"),
        IntegerField("dep2", label="Рефлексия 2"),
        IntegerField("dep3", label="Рефлексия 3"),
        IntegerField("dep4", label="Рефлексия 4"),
        IntegerField("dep5", label="Рефлексия 5"),
        IntegerField("dep_total", label="Рефлексия итого"),
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
        IntegerField("game_group_id", label="game_group_id"),
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


class GameResultView(ModelView):
    model = GameResult
    name = 'Результат игры'
    label = 'Результаты игр'

    fields = [
        "id",
        UserFullNameField(name="user_full_name", label="Пользователь"),
        IntegerField("game_id", label="игра"),
    IntegerField("score", label="Очки"),
    DateField(name="finished_at", label="Дата прохождения"),
    ]