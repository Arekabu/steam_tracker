from django.urls import path

from tracker import views

app_name = "tracker"

urlpatterns = [
    path("", views.game_list, name="game_list"),
    path("parse/", views.parse_games, name="parse_games"),
]
