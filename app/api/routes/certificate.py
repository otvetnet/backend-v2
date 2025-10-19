# Словарь цветов для каждой игры
GAME_COLORS = {
	"Где я - там и выбор": {
		"bg_color": "#003087",
		"svg_color1": "#FC610D",
		"svg_color2": "#FF00E5",
		"svg_color3": "#4FCD32"
	},
	"Не вестись — это выбор": {
		"bg_color": "#FC610D",
		"svg_color1": "#4FCD32",
		"svg_color2": "#1161F1",
		"svg_color3": "#FFCC00"
	},
	"Высоко — не значит круто": {
		"bg_color": "#FFA007",
		"svg_color1": "#4FCD32",
		"svg_color2": "#1161F1",
		"svg_color3": "#FF1E00"
	},
	"Кажется, что-то не так…": {
		"bg_color": "#4FCD32",
		"svg_color1": "#FC610D",
		"svg_color2": "#1161F1",
		"svg_color3": "#FF1E00"
	},
	"Когда не хочется молчать": {
		"bg_color": "#FF00E5",
		"svg_color1": "#FFA007",
		"svg_color2": "#4FCD32",
		"svg_color3": "#1161F1"
	}
}
# Словарь соответствий для названий игр
GAME_TITLES = {
	"game_1": "Где я - там и выбор",
	"game_2": "Не вестись — это выбор",
	"game_3": "Высоко — не значит круто",
	"game_4": "Кажется, что-то не так…",
	"game_5": "Когда не хочется молчать"
}
from fastapi import APIRouter, Response, Body
from pydantic import BaseModel

router = APIRouter()
import os
from weasyprint import HTML


# Pydantic-модель для входных данных
class CertificateRequest(BaseModel):
	last_name: str
	first_name: str
	game_name: str
	bg_color: str = None
	svg_color1: str = None
	svg_color2: str = None
	svg_color3: str = None

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), '../../templates/index.html')
BASE_URL = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../templates'))


@router.post('/certificate/pdf')
async def generate_certificate_pdf(
	data: CertificateRequest = Body(...)
):
	# Чтение HTML шаблона
	with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
		html_content = f.read()
	# Подстановка переменных
	html_content = html_content.replace('{{ last_name }}', data.last_name)
	html_content = html_content.replace('{{ first_name }}', data.first_name)
	html_content = html_content.replace('{{ game_name }}', data.game_name)
	# Получаем цвета для игры
	colors = GAME_COLORS.get(data.game_name, GAME_COLORS["Где я - там и выбор"])
	html_content = html_content.replace('{{ bg_color }}', data.bg_color or colors["bg_color"])
	html_content = html_content.replace('{{ svg_color1 }}', data.svg_color1 or colors["svg_color1"])
	html_content = html_content.replace('{{ svg_color2 }}', data.svg_color2 or colors["svg_color2"])
	html_content = html_content.replace('{{ svg_color3 }}', data.svg_color3 or colors["svg_color3"])
	pdf = HTML(string=html_content, base_url=BASE_URL).write_pdf(zoom=1)
	headers = {
		"Content-Disposition": "attachment; filename=certificate.pdf"
	}
	return Response(content=pdf, media_type="application/pdf", headers=headers)
