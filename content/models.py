from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    release_date = models.DateField()
    duration = models.IntegerField(help_text="Duration in minutes")
    rating = models.DecimalField(max_digits=3, decimal_places=1, validators=[MinValueValidator(0), MaxValueValidator(10)])
    poster = models.ImageField(upload_to='posters/', null=True, blank=True)
    trailer_url = models.URLField(blank=True)
    genres = models.ManyToManyField(Genre, related_name='movies')
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']


class TVShow(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    release_date = models.DateField()
    rating = models.DecimalField(max_digits=3, decimal_places=1, validators=[MinValueValidator(0), MaxValueValidator(10)])
    poster = models.ImageField(upload_to='posters/', null=True, blank=True)
    trailer_url = models.URLField(blank=True)
    genres = models.ManyToManyField(Genre, related_name='tvshows')
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']


class Episode(models.Model):
    tv_show = models.ForeignKey(TVShow, on_delete=models.CASCADE, related_name='episodes')
    season_number = models.PositiveIntegerField()
    episode_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField()
    duration = models.IntegerField(help_text="Duration in minutes")
    video_url = models.URLField()
    release_date = models.DateField()
    
    def __str__(self):
        return f"{self.tv_show.title} - S{self.season_number}E{self.episode_number}: {self.title}"
    
    class Meta:
        ordering = ['season_number', 'episode_number']
        unique_together = ['tv_show', 'season_number', 'episode_number']


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    bio = models.TextField(blank=True)
    favorite_genres = models.ManyToManyField(Genre, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, null=True, blank=True)
    tv_show = models.ForeignKey(TVShow, on_delete=models.CASCADE, null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = [
            ['user', 'movie'],
            ['user', 'tv_show']
        ]
    
    def __str__(self):
        if self.movie:
            return f"{self.user.username} - {self.movie.title}"
        return f"{self.user.username} - {self.tv_show.title}"


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, null=True, blank=True, related_name='reviews')
    tv_show = models.ForeignKey(TVShow, on_delete=models.CASCADE, null=True, blank=True, related_name='reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        if self.movie:
            return f"{self.user.username} - {self.movie.title} ({self.rating}/5)"
        return f"{self.user.username} - {self.tv_show.title} ({self.rating}/5)"
    
    class Meta:
        unique_together = [
            ['user', 'movie'],
            ['user', 'tv_show']
        ]


class Profile(models.Model):
    """Streaming profile that belongs to a user (Who's Watching selection)."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profiles')
    name = models.CharField(max_length=50)
    avatar_image = models.ImageField(upload_to='profile_avatars/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.username} - {self.name}"


class ProfileWatchlist(models.Model):
    """Watchlist entries associated with a specific profile."""
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='watchlist')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, null=True, blank=True)
    tv_show = models.ForeignKey(TVShow, on_delete=models.CASCADE, null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [
            ['profile', 'movie'],
            ['profile', 'tv_show']
        ]
        ordering = ['-added_at']

    def __str__(self):
        if self.movie:
            return f"{self.profile} - {self.movie.title}"
        return f"{self.profile} - {self.tv_show.title}"