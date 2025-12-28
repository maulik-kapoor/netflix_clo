from django.contrib import admin
from django.utils.html import format_html
from .models import Genre, Movie, TVShow, Episode, UserProfile, Watchlist, Review


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'movie_count', 'tvshow_count']
    search_fields = ['name', 'description']
    list_filter = ['name']
    
    def movie_count(self, obj):
        return obj.movies.count()
    movie_count.short_description = 'Movies'
    
    def tvshow_count(self, obj):
        return obj.tvshows.count()
    tvshow_count.short_description = 'TV Shows'


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['title', 'release_date', 'rating', 'duration', 'featured', 'genre_list', 'poster_preview']
    list_filter = ['featured', 'genres', 'release_date']
    search_fields = ['title', 'description']
    filter_horizontal = ['genres']
    date_hierarchy = 'release_date'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'release_date', 'duration')
        }),
        ('Media', {
            'fields': ('poster', 'trailer_url')
        }),
        ('Classification', {
            'fields': ('rating', 'genres', 'featured')
        }),
    )
    
    def genre_list(self, obj):
        return ', '.join([genre.name for genre in obj.genres.all()])
    genre_list.short_description = 'Genres'
    
    def poster_preview(self, obj):
        if obj.poster:
            return format_html('<img src="{}" width="50" height="75" style="border-radius: 4px;">', obj.poster.url)
        return 'No Image'
    poster_preview.short_description = 'Poster'


@admin.register(TVShow)
class TVShowAdmin(admin.ModelAdmin):
    list_display = ['title', 'release_date', 'rating', 'featured', 'genre_list', 'episode_count', 'poster_preview']
    list_filter = ['featured', 'genres', 'release_date']
    search_fields = ['title', 'description']
    filter_horizontal = ['genres']
    date_hierarchy = 'release_date'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'release_date')
        }),
        ('Media', {
            'fields': ('poster', 'trailer_url')
        }),
        ('Classification', {
            'fields': ('rating', 'genres', 'featured')
        }),
    )
    
    def genre_list(self, obj):
        return ', '.join([genre.name for genre in obj.genres.all()])
    genre_list.short_description = 'Genres'
    
    def episode_count(self, obj):
        return obj.episodes.count()
    episode_count.short_description = 'Episodes'
    
    def poster_preview(self, obj):
        if obj.poster:
            return format_html('<img src="{}" width="50" height="75" style="border-radius: 4px;">', obj.poster.url)
        return 'No Image'
    poster_preview.short_description = 'Poster'


@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ['title', 'tv_show', 'season_number', 'episode_number', 'duration', 'release_date']
    list_filter = ['tv_show', 'season_number', 'release_date']
    search_fields = ['title', 'description', 'tv_show__title']
    ordering = ['tv_show', 'season_number', 'episode_number']
    
    fieldsets = (
        ('Episode Information', {
            'fields': ('tv_show', 'season_number', 'episode_number', 'title', 'description')
        }),
        ('Media', {
            'fields': ('duration', 'video_url', 'release_date')
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'favorite_genres_list']
    list_filter = ['created_at', 'favorite_genres']
    search_fields = ['user__username', 'user__email', 'bio']
    filter_horizontal = ['favorite_genres']
    
    def favorite_genres_list(self, obj):
        return ', '.join([genre.name for genre in obj.favorite_genres.all()])
    favorite_genres_list.short_description = 'Favorite Genres'


@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'content_type', 'content_title', 'added_at']
    list_filter = ['added_at', 'movie', 'tv_show']
    search_fields = ['user__username', 'movie__title', 'tv_show__title']
    ordering = ['-added_at']
    
    def content_type(self, obj):
        if obj.movie:
            return 'Movie'
        elif obj.tv_show:
            return 'TV Show'
        return 'Unknown'
    content_type.short_description = 'Type'
    
    def content_title(self, obj):
        if obj.movie:
            return obj.movie.title
        elif obj.tv_show:
            return obj.tv_show.title
        return 'Unknown'
    content_title.short_description = 'Title'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'content_type', 'content_title', 'rating', 'created_at']
    list_filter = ['rating', 'created_at', 'movie', 'tv_show']
    search_fields = ['user__username', 'comment', 'movie__title', 'tv_show__title']
    ordering = ['-created_at']
    
    def content_type(self, obj):
        if obj.movie:
            return 'Movie'
        elif obj.tv_show:
            return 'TV Show'
        return 'Unknown'
    content_type.short_description = 'Type'
    
    def content_title(self, obj):
        if obj.movie:
            return obj.movie.title
        elif obj.tv_show:
            return obj.tv_show.title
        return 'Unknown'
    content_title.short_description = 'Title'


# Customize admin site
admin.site.site_header = "Netflix Clone Administration"
admin.site.site_title = "Netflix Clone Admin"
admin.site.index_title = "Welcome to Netflix Clone Administration"
