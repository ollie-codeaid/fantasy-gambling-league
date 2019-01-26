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
    )
]
