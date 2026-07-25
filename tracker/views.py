import logging

from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from tracker.models import Game

logger = logging.getLogger(__name__)


def game_list(request: HttpRequest) -> HttpResponse:
    """Отображает список всех игр с пагинацией"""

    # Получаем все игры, сортированные по убыванию игроков
    games = Game.objects.all()

    # Логируем запрос
    logger.info(f"📊 Запрошена страница со списком игр. Всего игр: {games.count()}")

    # Пагинация 20 игр на страницу
    paginator = Paginator(games, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "total_games": games.count(),
        "last_update": games.first().updated_at if games.exists() else None,
    }

    logger.info(
        f"📄 Отображена страница {page_number if page_number else 1} из {paginator.num_pages}"
    )

    return render(request, "tracker/game_list.html", context)
