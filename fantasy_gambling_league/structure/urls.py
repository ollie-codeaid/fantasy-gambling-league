from django.urls import path

from . import views

app_name = 'structure'
urlpatterns = [
    path('season/create/', views.SeasonCreateView.as_view(), name='create-season'),
    path(
        'season/update/<slug:slug>/',
        views.SeasonUpdateView.as_view(),
        name='update-season'
    ),
    path(
        'season/delete/<slug:slug>/',
        views.SeasonDeleteView.as_view(),
        name='delete-season'
    ),
    path('seasons/', views.SeasonListView.as_view(), name='list-seasons'),
    path('season/detail/<slug:slug>/',
        views.SeasonDetailView.as_view(),
        name='detail-season',
    ),
    path(
        'season/<slug:season_slug>/add_gameweek/',
        views.GameweekCreateView.as_view(),
        name='create-gameweek',
    ),
    path(
        'season/<slug:season_slug>/update/<int:number>/',
        views.GameweekUpdateView.as_view(),
        name='update-gameweek',
    ),
    path(
        'season/<slug:season_slug>/delete/<int:number>/',
        views.GameweekDeleteView.as_view(),
        name='delete-gameweek',
    ),
    path(
        'season/<slug:season_slug>/detail/<int:number>/',
        views.GameweekDetailView.as_view(),
        name='detail-gameweek',
    ),
]
