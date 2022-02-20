from django.shortcuts import render
from datetime import datetime

from django.db.models import Count, Window, F
from django.db.models.functions import DenseRank
from app.api.serializers import MovieSerializer
from app.app import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

import requests

from .models import Movie
# Create your views here.


class MoviesView(APIView):
    def post(self, request, format=None):

        # Get ther users  Input
        movie_title = request.data.get('movie_title')

        # Validate  Input
        if not movie_title:
            response = {
                'error': 'Please provide a movie title'
            }
            return Response(response, status.HTTP_400_BAD_REQUEST)

        # Fetch movie from API
        payload = {
            'apikey': settings.OMDB_API_KEY,
            't': movie_title
        }
        url = 'http://www.omdbapi.com'

        r = requests.get(url, params=payload)
        r = r.json()

        # Validate movie exists in API
        if r.get('Response') == 'False':
            response = {
                'error': f'There is no movie like {movie_title}'
            }
            return Response(response, status.HTTP_400_BAD_REQUEST)

        # Validate duplicate movie doesn't exist in DB
        if r.get('imdbID') in [str(q) for q in Movie.get_all()]:
            response = {
                'error': f'{movie_title} already exists in DB'
            }
            return Response(response, status.HTTP_400_BAD_REQUEST)

        # Save Fetched movie from API to DB
        movie = Movie()
        for key, value in r.items():

            # not saving Year Ratings and Response due to being duplicate
            if key == 'Year' or key == 'Ratings' or key == 'Response':
                continue

            # For Date fields, Convert to date type
            elif key == 'Released' or key == 'DVD':
                value = datetime.strptime(
                    value, '%d %b %Y').date() if value != 'N/A' else None

            # For Int and Decimal types, convert and Remove '$' and ','
            elif key == 'imdbVotes' or key == 'BoxOffice' or key == 'Metascore':
                if ',' in value:
                    value = value.replace(',', '')
                if '$' in value:
                    value = value.replace('$', '')
                value = int(value) if value != 'N/A' else 0
            elif key == 'imdbRating':
                value = float(value) if value != 'N/A' else 0

            key = key.lower()

            setattr(movie, key, value)
        movie.save()

        serializer = MovieSerializer(movie)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, format=None):

        order_by = request.GET.get('order_by')
        desc = request.GET.get('desc')

        # change to 'imdbrating' if 'rating' is provided
        order_by = 'imdbrating' if order_by == 'rating' else order_by

        # Send movies without ordering if order_by not provided
        if not order_by:
            # return all_json_response(Movie)
            serializer = MovieSerializer(Movie.get_all(), many=True)
            return Response(serializer.data)
        else:
           
            # order_by accepts'title' and 'rating' only
            if order_by != 'imdbrating' and order_by != 'title':
                order_by = 'id'  # defaults to order_by id

            if desc == 'true':
                order_by = '-' + order_by

            qs = Movie.get_all().order_by(order_by)

            serializer = MovieSerializer(qs, many=True)
            return Response(serializer.data)
