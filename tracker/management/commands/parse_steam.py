import logging

import requests
from django.core.management.base import BaseCommand
from django.db import transaction

from tracker.models import Game

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Парсит топ-100 игр Steam по игрокам за 2 недели и сохраняет в БД"

    def handle(self, *args: object, **options: object) -> None:
        self.stdout.write(self.style.SUCCESS("🚀 Начинаю парсинг Steam API..."))
        logger.info("🚀 Начинаю парсинг Steam API")

        try:
            # Получаем топ за 2 недели
            url = "https://steamspy.com/api.php?request=top100in2weeks"
            logger.info(f"📡 Отправляю запрос к SteamSpy API: {url}")

            response = requests.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()
            logger.info(f"✅ Получено {len(data)} игр от API")
            self.stdout.write(f"✅ Получено {len(data)} игр")

            # Логируем структуру данных для отладки
            if data:
                first_appid = next(iter(data.keys()))
                first_game = data[first_appid]
                logger.info(f"🔍 Доступные поля: {list(first_game.keys())}")
                self.stdout.write(f"🔍 Доступные поля: {list(first_game.keys())}")

            with transaction.atomic():
                for appid, game_data in data.items():
                    # Извлекаем CCU (пиковый онлайн)
                    ccu = game_data.get("ccu", 0)
                    if isinstance(ccu, str):
                        ccu = int(ccu.replace(",", "")) if ccu else 0

                    # Извлекаем owners (диапазон владельцев)
                    owners = game_data.get("owners", "")

                    Game.objects.update_or_create(
                        appid=int(appid),
                        defaults={
                            "name": game_data.get("name", "Unknown"),
                            "developer": game_data.get("developer", ""),
                            "publisher": game_data.get("publisher", ""),
                            "owners": owners,
                            "ccu": ccu,
                        },
                    )

                    logger.info(
                        f"🎮 Сохранена игра: {game_data.get('name')} (ID: {appid}) - "
                        f"CCU: {ccu}, Владельцев: {owners}"
                    )

                count = Game.objects.count()
                logger.info(f"💾 В базе данных теперь {count} игр")
                self.stdout.write(
                    self.style.SUCCESS(f"💾 Успешно сохранено! Всего игр в БД: {count}")
                )

                # Логируем топ-5 по CCU
                top_games = Game.objects.order_by("-ccu")[:5]
                self.stdout.write(
                    self.style.SUCCESS("\n🏆 Топ-5 игр по пиковому онлайну (CCU):")
                )
                for i, game in enumerate(top_games, 1):
                    self.stdout.write(
                        f"  {i}. {game.name} - {game.ccu:,} игроков (CCU)"
                    )
                    logger.info(f"🏆 Топ-{i}: {game.name} - CCU: {game.ccu}")

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Ошибка при запросе к Steam API: {e!s}")
            self.stdout.write(self.style.ERROR(f"❌ Ошибка API: {e!s}"))

        except Exception as e:
            logger.exception("❌ Непредвиденная ошибка при парсинге Steam API")
            self.stdout.write(self.style.ERROR(f"❌ Ошибка: {e!s}"))
