import os

from django.contrib.auth.models import Group, Permission, User
from django.core.management.base import BaseCommand

from movies.models import Genre, Movie, Person, Rating

GENRES = ['Acción', 'Drama', 'Comedia', 'Ciencia ficción']

MOVIES = [
    ('Matrix', 1999, 'Ciencia ficción', 'Acción'),
    ('Blade Runner 2049', 2017, 'Ciencia ficción', 'Drama'),
    ('Interestelar', 2014, 'Ciencia ficción', 'Drama'),
    ('Mad Max: Furia en el camino', 2015, 'Acción', 'Ciencia ficción'),
    ('John Wick', 2014, 'Acción'),
    ('El padrino', 1972, 'Drama'),
    ('Forrest Gump', 1994, 'Drama', 'Comedia'),
    ('Superbad', 2007, 'Comedia'),
    ('Una noche en el museo', 2006, 'Comedia', 'Acción'),
    ('Parásitos', 2019, 'Drama', 'Comedia'),
]

RATINGS = {
    'Matrix': [('Ana', 10), ('Luis', 9), ('Marta', 9)],
    'Blade Runner 2049': [('Ana', 8), ('Luis', 9)],
    'Interestelar': [('Marta', 10), ('Carlos', 9)],
    'Mad Max: Furia en el camino': [('Luis', 8), ('Carlos', 9)],
    'El padrino': [('Ana', 10), ('Marta', 10), ('Luis', 9)],
    'Forrest Gump': [('Carlos', 8)],
    'Parásitos': [('Ana', 9), ('Luis', 10)],
}


class Command(BaseCommand):
    help = 'Load demo data, the "editores" group and the demo users.'

    def handle(self, *args, **options):
        genres = {n: Genre.objects.get_or_create(name=n)[0] for n in GENRES}
        director, _ = Person.objects.get_or_create(name='Director de ejemplo')

        for title, year, *genre_names in MOVIES:
            movie, _ = Movie.objects.get_or_create(
                title=title, year=year, defaults={'director': director}
            )
            movie.genres.set([genres[g] for g in genre_names])
            for reviewer, score in RATINGS.get(title, []):
                Rating.objects.get_or_create(
                    movie=movie, reviewer=reviewer, defaults={'score': score}
                )

        # Group: can add and change movies, cannot delete them.
        group, _ = Group.objects.get_or_create(name='editores')
        perms = Permission.objects.filter(
            content_type__app_label='movies',
            codename__in=['add_movie', 'change_movie', 'view_movie'],
        )
        group.permissions.set(perms)

        admin_pwd = os.environ.get('DEMO_ADMIN_PASSWORD', 'Admin12345!')
        editor_pwd = os.environ.get('DEMO_EDITOR_PASSWORD', 'Editor12345!')

        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', admin_pwd)
        editor, created = User.objects.get_or_create(
            username='editor1', defaults={'is_staff': True}
        )
        if created:
            editor.set_password(editor_pwd)
        editor.is_staff = True
        editor.save()
        editor.groups.add(group)

        self.stdout.write(self.style.SUCCESS(
            f'Demo ready: {Movie.objects.count()} movies, '
            f'{Genre.objects.count()} genres, {Rating.objects.count()} ratings.'
        ))
