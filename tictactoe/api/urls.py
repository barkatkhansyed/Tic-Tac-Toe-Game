from django.urls import path
from . import views


urlpatterns = [
    path(r'move', views.Move.as_view(), name='game-updates'),
    path(r'move/<int:row>/<int:column>', views.Move.as_view(), name='move'),
    path(r'get_high_score_list',  views.GetHighScoreList, name='GetHighScore')
]