from django.urls import path

from . import views

app_name = 'api'
urlpatterns = [

    path('movies', views.MoviesView.as_view(), name='movies'),
    path('comments', views.CommentsView.as_view(), name='comments'),
    path('top-rated-movie', views.TopRatedMovieView.as_view(),
         name='top-rated-movie'),
]
