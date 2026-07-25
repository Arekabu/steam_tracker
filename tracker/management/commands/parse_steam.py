import logging

import requests
from django.core.management.base import BaseCommand
from django.db import transaction

from tracker.models import Game

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Парсит топ-100 игр Steam и сохраняет в БД"

    def handle(self, *args: object, **options: object) -> None:
        self.stdout.write(self.style.SUCCESS("🚀 Начинаю парсинг Steam API..."))
        logger.info("🚀 Начинаю парсинг Steam API")

        try:
            # Получаем топ за 2 недели
            url_2weeks = "https://steamspy.com/api.php?request=top100in2weeks"
            logger.info(f"📡 Отправляю запрос к SteamSpy API: {url_2weeks}")

            response = requests.get(url_2weeks, timeout=10)
            response.raise_for_status()

            data = response.json()
            logger.info(f"✅ Получено {len(data)} игр от API")
            self.stdout.write(f"✅ Получено {len(data)} игр")

            # Сохраняем игры в БД
            with transaction.atomic():
                for appid, game_data in data.items():
                    Game.objects.update_or_create(
                        appid=int(appid),
                        defaults={
                            "name": game_data.get("name", "Unknown"),
                            "players_2weeks": game_data.get("players_2weeks", 0),
                            "players_forever": game_data.get("players_forever", 0),
                        },
                    )

                    # Логируем каждую игру
                    logger.info(
                        f"🎮 Сохранена игра: {game_data.get('name')} (ID: {appid})"
                    )

                count = Game.objects.count()
                logger.info(f"💾 В базе данных теперь {count} игр")
                self.stdout.write(
                    self.style.SUCCESS(f"💾 Успешно сохранено! Всего игр в БД: {count}")
                )

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Ошибка при запросе к Steam API: {e!s}")
            self.stdout.write(self.style.ERROR(f"❌ Ошибка API: {e!s}"))

        except Exception as e:
            logger.exception("❌ Непредвиденная ошибка при парсинге Steam API")
            self.stdout.write(self.style.ERROR(f"❌ Ошибка: {e!s}"))
