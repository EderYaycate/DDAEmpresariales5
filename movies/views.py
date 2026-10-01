from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404, render

from .models import Genre, Movie


def genre_list(request):
    genres = Genre.objects.annotate(total=Count('movies')).order_by('name')
    return render(request, 'movies/genre_list.html', {'genres': genres})


def recommendations(request, genre_id):
    """Top-rated movies of a genre (only movies that have ratings)."""
    genre = get_object_or_404(Genre, pk=genre_id)
    movies = (
        Movie.objects.filter(genres=genre)
        .annotate(avg_score=Avg('ratings__score'), total_ratings=Count('ratings'))
        .filter(total_ratings__gt=0)
        .order_by('-avg_score', '-total_ratings', 'title')[:5]
    )
    return render(
        request, 'movies/recommendations.html', {'genre': genre, 'movies': movies}
    )
