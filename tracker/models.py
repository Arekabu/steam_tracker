from typing import ClassVar

from django.db import models


class Game(models.Model):
    appid = models.IntegerField(unique=True, verbose_name="ID игры")
    name = models.CharField(max_length=255, verbose_name="Название")
    players_2weeks = models.IntegerField(default=0, verbose_name="Игроков за 2 недели")
    players_forever = models.IntegerField(
        default=0, verbose_name="Игроков за всё время"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        ordering: ClassVar[list[str]] = ["-players_2weeks"]
        verbose_name = "Игра"
        verbose_name_plural = "Игры"

    def __str__(self) -> str:
        return f"{self.name} ({self.players_2weeks} игроков)"
