from datetime import date

from django.db.models import Count, Window, F
from django.db.models.functions import DenseRank
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from api.models import Movie, Comment
from api.serializers import MovieSerializer, CommentSerializer, TopMovieSerializer


class MoviesTests(TestCase):
    fixtures = ['test_data.json']

    def test_post_movie(self):
        """
        POST /movies successfully posts a movie with a title
        :return: new movie as json
        """
        r = self.client.post(reverse('api:movies'), {
                             'movie_title': 'fight club'})

        self.assertEqual(r.status_code, 201)

    def test_post_movie_without_data(self):
        """
        POST /movies without data, returns error
        :return: {"error": "Please provide a movie title"}
        """

        r = self.client.post(reverse('api:movies'))
        self.assertJSONEqual(
            r.content,
            '{"error": "Please provide a movie title"}'
        )
        self.assertEqual(r.status_code, 400)

    def test_post_movie_not_exist_in_api(self):
        """
        POST /movies with some garbage movie title name
        :return: "error": "There is no movie like fight clubqwerasdfasrwer"
        """

        r = self.client.post(reverse('api:movies'), {
                             'movie_title': 'fight clubqwerasdfasrwer'})
        self.assertJSONEqual(
            r.content,
            '{"error": "There is no movie like fight clubqwerasdfasrwer"}'
        )
        self.assertEqual(r.status_code, 400)

   
    def test_get_movies(self):
        """
        GET /movies gets all movies
        :return: all movies in json
        """

        all_values = Movie.get_all()
        serializer = MovieSerializer(all_values, many=True)

        r = self.client.get(reverse('api:movies'))
        self.assertJSONEqual(
            r.content,
            serializer.data
        )
        self.assertEqual(r.status_code, 200)

    def test_get_movies_order_by_rating(self):
        """
        GET /movies provided with order_by=rating param
        :return: all movies ordered_by rating asc
        """

        r = self.client.get(reverse('api:movies'), {'order_by': 'rating'})

        qs = Movie.get_all().order_by('imdbrating')
        serializer = MovieSerializer(qs, many=True)

        self.assertJSONEqual(
            r.content,
            serializer.data
        )
        self.assertEqual(r.status_code, 200)

    def test_get_movies_order_by_rating_desc(self):
        """
        GET /movies provided with order_by=rating and desc=true params
        :return: all movies ordered_by rating desc
        """

        r = self.client.get(reverse('api:movies'), {
                            'order_by': 'rating', 'desc': 'true'})

        qs = Movie.get_all().order_by('-imdbrating')
        serializer = MovieSerializer(qs, many=True)

        self.assertJSONEqual(
            r.content,
            serializer.data
        )
        self.assertEqual(r.status_code, 200)

    def test_get_movies_order_by_title(self):
        """
        GET /movies provided with order_by=title param
        :return: all movies ordered by title asc
        """

        r = self.client.get(reverse('api:movies'), {'order_by': 'title'})

        qs = Movie.get_all().order_by('title')
        serializer = MovieSerializer(qs, many=True)

        self.assertJSONEqual(
            r.content,
            serializer.data
        )
        self.assertEqual(r.status_code, 200)

    def test_get_movies_order_by_title_desc(self):
        """
        GET /movies provided with order_by=title and desc=true params
        :return: all movies ordered by title desc
        """

        r = self.client.get(reverse('api:movies'), {
                            'order_by': 'title', 'desc': 'true'})

        qs = Movie.get_all().order_by('-title')
        serializer = MovieSerializer(qs, many=True)

        self.assertJSONEqual(
            r.content,
            serializer.data
        )
        self.assertEqual(r.status_code, 200)

    def test_get_movie_top_all(self):
        """
        GET /top movies ordered by rank on total comments
        :return: result in json
        """

        r = self.client.get(reverse('api:top-rated-movie'))

        qs = Movie.objects \
            .annotate(total_comments=Count('comment__comment'),
                      rank=Window(
                          expression=DenseRank(),
                          order_by=F('total_comments').desc(),
            )
            ).values('id', 'total_comments', 'rank')

        serializer = TopMovieSerializer(qs, many=True)

        self.assertJSONEqual(
            r.content,
            serializer.data
        )
        self.assertEqual(r.status_code, 200)

    def test_get_movie_top_date_range(self):
        """
        GET /top get top movies ordered by rank on total comments and filtered by specified date range
        :return: the result in json
        """

        start_date = date(2019, 5, 22)
        end_date = date(2019, 5, 25)

        r = self.client.get(reverse('api:top-rated-movie'), {
                            'start_date': start_date, 'end_date': end_date})

        qs = Movie.objects \
            .filter(comment__added_on__range=(start_date, end_date)) \
            .annotate(total_comments=Count('comment__comment'),
                      rank=Window(
                          expression=DenseRank(),
                          order_by=F('total_comments').desc(),
            )
            ).values('id', 'total_comments', 'rank')

        serializer = TopMovieSerializer(qs, many=True)

        self.assertJSONEqual(
            r.content,
            serializer.data
        )
        self.assertEqual(r.status_code, 200)


class CommentTests(TestCase):
    fixtures = ['test_data.json']

    def test_post_comment_user_data_validation(self):
        """
        POST /comments user data validation
        :return: error message
        """

        # omit both input
        r1 = self.client.post(reverse('api:comments'))
        self.assertJSONEqual(
            r1.content,
            '{"error": "Please provide movie ID and comment"}'
        )
        self.assertEqual(r1.status_code, 400)

        # omit only comment
        r2 = self.client.post(reverse('api:comments'), {
                              'movie_id': 'tt0112573'})
        self.assertJSONEqual(
            r2.content,
            '{"error": "Please provide movie ID and comment"}'
        )
        self.assertEqual(r2.status_code, 400)

        r3 = self.client.post(reverse('api:comments'), {
                              'comment': 'test comment'})
        self.assertJSONEqual(
            r3.content,
            '{"error": "Please provide movie ID and comment"}'
        )
        self.assertEqual(r3.status_code, 400)

    def test_post_comment_movie__dose_not_exist(self):
        """
        POST /comments movie doesn't exist for the comment
        :return: error message
        """

        r = self.client.post(reverse('api:comments'), {
                             'movie_id': 'testid', 'comment': 'test_comment'})
        self.assertJSONEqual(
            r.content,
            '{"error": "Movie with movie id testid, doesn\'t exist in DB. Make sure to enter imdb id"}'
        )
        self.assertEqual(r.status_code, 400)

  

    def test_get_comment_all(self):
        """
        GET /comments successful get
        :return: get all comments
        """

        r = self.client.get(reverse('api:comments'))

        all_values = Comment.get_all()
        serializer = CommentSerializer(all_values, many=True)

        self.assertJSONEqual(
            r.content,
            serializer.data
        )
        self.assertEqual(r.status_code, 200)

    def test_get_comment_by_movieid(self):
        """
        GET /comments with a movie id param
        :return: all comments related to a movie
        """

        movie_id = 'tt1737174'

        r = self.client.get(reverse('api:comments'),
                            {'movie_id': movie_id})

        qs = Comment.objects.filter(movie__imdbid=movie_id)
        serializer = CommentSerializer(qs, many=True)

        self.assertJSONEqual(
            r.content,
            serializer.data
        )
        self.assertEqual(r.status_code, 200)
