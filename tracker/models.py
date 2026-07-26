from typing import ClassVar

from django.db import models


class Game(models.Model):
    appid = models.IntegerField(unique=True, verbose_name="ID игры")
    name = models.CharField(max_length=255, verbose_name="Название")
    developer = models.CharField(max_length=255, blank=True, verbose_name="Разработчик")
    publisher = models.CharField(max_length=255, blank=True, verbose_name="Издатель")
    owners = models.CharField(
        max_length=100, blank=True, verbose_name="Владельцы (диапазон)"
    )
    ccu = models.IntegerField(default=0, verbose_name="Пиковый онлайн (CCU)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        ordering: ClassVar[list[str]] = ["-ccu"]
        verbose_name = "Игра"
        verbose_name_plural = "Игры"

    def __str__(self) -> str:
        return f"{self.name} (CCU: {self.ccu})"
