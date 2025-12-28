from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('profiles/', views.profile_select, name='profile_select'),
    path('profiles/use/<int:profile_id>/', views.profile_use, name='profile_use'),
    path('movie/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('tv-show/<int:tvshow_id>/', views.tvshow_detail, name='tvshow_detail'),
    path('episode/<int:episode_id>/', views.episode_detail, name='episode_detail'),
    path('search/', views.search, name='search'),
    path('genre/<int:genre_id>/', views.genre_view, name='genre_view'),
    path('watchlist/', views.watchlist_view, name='watchlist'),
    path('watchlist/add/', views.add_to_watchlist, name='add_to_watchlist'),
    path('watchlist/remove/', views.remove_from_watchlist, name='remove_from_watchlist'),
    path('review/add/', views.add_review, name='add_review'),
]
