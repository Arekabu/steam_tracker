import logging
from datetime import UTC, datetime, timedelta

from django.contrib import messages
from django.core.management import call_command
from django.core.management.base import CommandError
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from tracker.models import Game

logger = logging.getLogger(__name__)


def game_list(request: HttpRequest) -> HttpResponse:
    """Отображает список всех игр с пагинацией"""
    games = Game.objects.all()
    logger.info(f"📊 Запрошена страница со списком игр. Всего игр: {games.count()}")

    paginator = Paginator(games, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    ccu_date = datetime.now(tz=UTC).date() - timedelta(days=1)

    context = {
        "page_obj": page_obj,
        "total_games": games.count(),
        "last_update": games.first().updated_at if games.exists() else None,
        "top_game": games.order_by("-ccu").first() if games.exists() else None,
        "ccu_date": ccu_date,
    }

    logger.info(
        f"📄 Отображена страница {page_number if page_number else 1} из {paginator.num_pages}"
    )

    return render(request, "tracker/game_list.html", context)


def parse_games(request: HttpRequest) -> HttpResponse:  # 👈 ДОБАВЬ ЭТУ ФУНКЦИЮ
    """Ручной запуск парсинга Steam API"""
    if request.method == "POST":
        try:
            logger.info("🔄 Ручное обновление данных через веб-интерфейс")
            call_command("parse_steam")
            messages.success(request, "✅ Данные успешно обновлены!")
            logger.info("✅ Ручное обновление данных завершено успешно")
        except CommandError as e:
            messages.error(request, f"❌ Ошибка выполнения команды: {e!s}")
            logger.exception("❌ Ошибка выполнения команды")
        except Exception as e:
            messages.error(request, f"❌ Непредвиденная ошибка: {e!s}")
            logger.exception("❌ Непредвиденная ошибка")

    return redirect("tracker:game_list")
