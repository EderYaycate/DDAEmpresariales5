from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class AuditModel(models.Model):
    """Abstract base with read-only audit timestamps."""

    created_at = models.DateTimeField('fecha de creación', auto_now_add=True)
    updated_at = models.DateTimeField('última modificación', auto_now=True)

    class Meta:
        abstract = True


class Genre(AuditModel):
    name = models.CharField('nombre', max_length=60, unique=True)

    class Meta:
        verbose_name = 'género'
        verbose_name_plural = 'géneros'
        ordering = ['name']

    def __str__(self):
        return self.name


class Person(AuditModel):
    name = models.CharField('nombre', max_length=120)
    birth_date = models.DateField('fecha de nacimiento', null=True, blank=True)
    photo = models.ImageField('foto', upload_to='people/', null=True, blank=True)

    class Meta:
        verbose_name = 'persona'
        verbose_name_plural = 'personas'
        ordering = ['name']

    def __str__(self):
        return self.name


class Movie(AuditModel):
    title = models.CharField('título', max_length=200)
    year = models.PositiveSmallIntegerField(
        'año',
        validators=[MinValueValidator(1888), MaxValueValidator(2100)],
    )
    synopsis = models.TextField('sinopsis', blank=True)
    poster = models.ImageField('póster', upload_to='posters/', null=True, blank=True)
    genres = models.ManyToManyField(Genre, related_name='movies', verbose_name='géneros')
    director = models.ForeignKey(
        Person,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='directed_movies',
        verbose_name='director',
    )

    class Meta:
        verbose_name = 'película'
        verbose_name_plural = 'películas'
        ordering = ['-year', 'title']

    def __str__(self):
        return f'{self.title} ({self.year})'


class Rating(AuditModel):
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name='ratings',
        verbose_name='película',
    )
    reviewer = models.CharField('evaluador', max_length=100)
    score = models.PositiveSmallIntegerField(
        'puntaje',
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    comment = models.TextField('comentario', blank=True)

    class Meta:
        verbose_name = 'valoración'
        verbose_name_plural = 'valoraciones'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.movie.title}: {self.score}/10 por {self.reviewer}'
