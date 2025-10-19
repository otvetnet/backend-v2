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
        IntegerField("q1", label="Вопрос 1"),
        IntegerField("q2", label="Вопрос 2"),
        IntegerField("q3", label="Вопрос 3"),
        IntegerField("q4", label="Вопрос 4"),
        IntegerField("q5", label="Вопрос 5"),
        IntegerField("g1_total", label="Итого 1"),
        IntegerField("q6", label="Вопрос 6"),
        IntegerField("q7", label="Вопрос 7"),
        IntegerField("q8", label="Вопрос 8"),
        IntegerField("q9", label="Вопрос 9"),
        IntegerField("q10", label="Вопрос 10"),
        IntegerField("g2_total", label="Итого 2"),
        IntegerField("q11", label="Вопрос 11"),
        IntegerField("q12", label="Вопрос 12"),
        IntegerField("q13", label="Вопрос 13"),
        IntegerField("q14", label="Вопрос 14"),
        IntegerField("q15", label="Вопрос 15"),
        IntegerField("g3_total", label="Итого 3"),
        IntegerField("q16", label="Вопрос 16"),
        IntegerField("q17", label="Вопрос 17"),
        IntegerField("q18", label="Вопрос 18"),
        IntegerField("q19", label="Вопрос 19"),
        IntegerField("q20", label="Вопрос 20"),
        IntegerField("g4_total", label="Итого 4"),
        IntegerField("q21", label="Вопрос 21"),
        IntegerField("q22", label="Вопрос 22"),
        IntegerField("q23", label="Вопрос 23"),
        IntegerField("q24", label="Вопрос 24"),
        IntegerField("q25", label="Вопрос 25"),
        IntegerField("g5_total", label="Итого 5"),
        IntegerField("q26", label="Вопрос 26"),
        IntegerField("q27", label="Вопрос 27"),
        IntegerField("q28", label="Вопрос 28"),
        IntegerField("q29", label="Вопрос 29"),
        IntegerField("q30", label="Вопрос 30"),
        IntegerField("g6_total", label="Итого 6"),
        IntegerField("dep_id", label="Игра"),
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