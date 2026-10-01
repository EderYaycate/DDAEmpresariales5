from django.contrib.auth.models import Group, Permission, User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import Genre, Movie


class AdminAndAccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('setup_demo', verbosity=0)

    def test_demo_data_counts(self):
        self.assertEqual(Movie.objects.count(), 10)
        self.assertEqual(Genre.objects.count(), 4)
        self.assertGreaterEqual(Movie.objects.filter(ratings__isnull=False).distinct().count(), 5)

    def test_superuser_sees_all_four_models(self):
        self.client.login(username='admin', password='Admin12345!')
        response = self.client.get('/admin/movies/')
        for model in ('movie', 'genre', 'person', 'rating'):
            self.assertContains(response, f'/admin/movies/{model}/')

    def test_editor_can_add_and_change_but_not_delete_movies(self):
        editor = User.objects.get(username='editor1')
        self.assertTrue(editor.has_perm('movies.add_movie'))
        self.assertTrue(editor.has_perm('movies.change_movie'))
        self.assertFalse(editor.has_perm('movies.delete_movie'))

    def test_editor_only_sees_movies_in_panel(self):
        self.client.login(username='editor1', password='Editor12345!')
        response = self.client.get('/admin/movies/')
        self.assertContains(response, '/admin/movies/movie/')
        for model in ('genre', 'person', 'rating'):
            self.assertNotContains(response, f'/admin/movies/{model}/')

    def test_editor_cannot_delete_a_movie(self):
        self.client.login(username='editor1', password='Editor12345!')
        movie = Movie.objects.first()
        response = self.client.post(f'/admin/movies/movie/{movie.pk}/delete/', {'post': 'yes'})
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Movie.objects.filter(pk=movie.pk).exists())

    def test_audit_fields_are_readonly(self):
        self.client.login(username='admin', password='Admin12345!')
        movie = Movie.objects.first()
        response = self.client.get(f'/admin/movies/movie/{movie.pk}/change/')
        self.assertNotContains(response, 'name="created_at"')
        self.assertNotContains(response, 'name="updated_at"')

    def test_rating_inline_in_movie_form(self):
        self.client.login(username='admin', password='Admin12345!')
        movie = Movie.objects.first()
        response = self.client.get(f'/admin/movies/movie/{movie.pk}/change/')
        self.assertContains(response, 'ratings-TOTAL_FORMS')


class RecommendationViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('setup_demo', verbosity=0)

    def test_recommendations_ordered_by_average(self):
        genre = Genre.objects.get(name='Drama')
        response = self.client.get(reverse('movies:recommendations', args=[genre.pk]))
        self.assertEqual(response.status_code, 200)
        movies = list(response.context['movies'])
        scores = [m.avg_score for m in movies]
        self.assertEqual(scores, sorted(scores, reverse=True))
        self.assertEqual(movies[0].title, 'El padrino')

    def test_genre_without_rated_movies_shows_empty_message(self):
        genre = Genre.objects.create(name='Documental')
        response = self.client.get(reverse('movies:recommendations', args=[genre.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['movies']), [])
        self.assertContains(response, 'Aún no hay películas valoradas')
