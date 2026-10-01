from django.contrib import admin

from .models import Genre, Movie, Person, Rating


class AuditAdminMixin:
    """Audit fields are shown but never editable."""

    readonly_fields = ('created_at', 'updated_at')


class RatingInline(admin.TabularInline):
    model = Rating
    extra = 1
    fields = ('reviewer', 'score', 'comment')


@admin.register(Genre)
class GenreAdmin(AuditAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


@admin.register(Person)
class PersonAdmin(AuditAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'birth_date')
    search_fields = ('name',)


@admin.register(Movie)
class MovieAdmin(AuditAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'year', 'director', 'genre_list', 'created_at')
    list_filter = ('genres', 'year')
    search_fields = ('title', 'director__name')
    filter_horizontal = ('genres',)
    list_select_related = ('director',)
    inlines = [RatingInline]

    @admin.display(description='géneros')
    def genre_list(self, obj):
        return ', '.join(g.name for g in obj.genres.all())

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('genres')


@admin.register(Rating)
class RatingAdmin(AuditAdminMixin, admin.ModelAdmin):
    list_display = ('movie', 'reviewer', 'score', 'created_at')
    list_filter = ('score', 'movie__genres')
    search_fields = ('movie__title', 'reviewer')
