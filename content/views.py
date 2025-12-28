from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import Movie, TVShow, Episode, Genre, Watchlist, Review, Profile, ProfileWatchlist
from django.conf import settings
import json
from urllib.parse import urlencode
from urllib.request import urlopen
from urllib.error import URLError, HTTPError


def home(request):
    """Home page with featured content and genre sections"""
    featured_movies = Movie.objects.filter(featured=True)[:6]
    featured_tvshows = TVShow.objects.filter(featured=True)[:6]
    genres = Genre.objects.all()[:8]
    
    # Get recent movies and TV shows
    recent_movies = Movie.objects.all()[:12]
    recent_tvshows = TVShow.objects.all()[:12]
    my_list_movies = []
    active_profile_id = request.session.get('active_profile_id')
    if request.user.is_authenticated and active_profile_id:
        my_list_movies = Movie.objects.filter(profilewatchlist__profile_id=active_profile_id).distinct()
    
    context = {
        'featured_movies': featured_movies,
        'featured_tvshows': featured_tvshows,
        'genres': genres,
        'recent_movies': recent_movies,
        'recent_tvshows': recent_tvshows,
        'my_list_movies': my_list_movies,
    }
    return render(request, 'content/home.html', context)


def movie_detail(request, movie_id):
    """Movie detail page"""
    movie = get_object_or_404(Movie, id=movie_id)
    reviews = Review.objects.filter(movie=movie).order_by('-created_at')[:5]
    is_in_watchlist = False
    active_profile_id = request.session.get('active_profile_id')
    if request.user.is_authenticated and active_profile_id:
        is_in_watchlist = ProfileWatchlist.objects.filter(profile_id=active_profile_id, movie=movie).exists()
    
    # Fetch TMDB data (best-effort) by searching title and year
    tmdb_data = {}
    tmdb_images = {}
    tmdb_videos = {}
    tmdb_poster_url = ''
    tmdb_backdrop_url = ''
    tmdb_trailer_url = ''
    api_key = getattr(settings, 'TMDB_API_KEY', '')
    if api_key and movie.title:
        try:
            search_params = {
                'api_key': api_key,
                'query': movie.title,
                'include_adult': 'false',
            }
            try:
                if movie.release_date:
                    search_params['year'] = movie.release_date.year
            except Exception:
                pass

            search_url = 'https://api.themoviedb.org/3/search/movie?' + urlencode(search_params)
            with urlopen(search_url, timeout=5) as resp:
                payload = json.loads(resp.read().decode('utf-8'))
            results = payload.get('results', [])
            if results:
                tmdb_match = results[0]
                tmdb_id = tmdb_match.get('id')
                if tmdb_id:
                    details_params = {'api_key': api_key, 'append_to_response': 'images,videos'}
                    details_url = f'https://api.themoviedb.org/3/movie/{tmdb_id}?' + urlencode(details_params)
                    with urlopen(details_url, timeout=5) as resp:
                        data = json.loads(resp.read().decode('utf-8'))
                    tmdb_data = data or {}
                    tmdb_images = tmdb_data.get('images', {})
                    tmdb_videos = tmdb_data.get('videos', {})

                    # Build helpful URLs for template
                    poster_path = tmdb_data.get('poster_path')
                    backdrop_path = tmdb_data.get('backdrop_path')
                    if poster_path:
                        tmdb_poster_url = f'https://image.tmdb.org/t/p/w500{poster_path}'
                    if backdrop_path:
                        tmdb_backdrop_url = f'https://image.tmdb.org/t/p/w1280{backdrop_path}'

                    # Find a trailer or teaser from YouTube
                    videos = (tmdb_videos or {}).get('results', [])
                    for video in videos:
                        if video.get('site') == 'YouTube' and video.get('key') and video.get('type') in ('Trailer', 'Teaser'):
                            tmdb_trailer_url = f"https://www.youtube.com/watch?v={video['key']}"
                            break
        except (URLError, HTTPError, TimeoutError, ValueError, Exception):
            # Swallow errors to avoid breaking page render
            tmdb_data = {}
            tmdb_images = {}
            tmdb_videos = {}
            tmdb_poster_url = ''
            tmdb_backdrop_url = ''
            tmdb_trailer_url = ''

    context = {
        'movie': movie,
        'reviews': reviews,
        'is_in_watchlist': is_in_watchlist,
        'tmdb': tmdb_data,
        'tmdb_images': tmdb_images,
        'tmdb_videos': tmdb_videos,
        'tmdb_poster_url': tmdb_poster_url,
        'tmdb_backdrop_url': tmdb_backdrop_url,
        'tmdb_trailer_url': tmdb_trailer_url,
    }
    return render(request, 'content/movie_detail.html', context)


def tvshow_detail(request, tvshow_id):
    """TV Show detail page"""
    tvshow = get_object_or_404(TVShow, id=tvshow_id)
    episodes = Episode.objects.filter(tv_show=tvshow).order_by('season_number', 'episode_number')
    reviews = Review.objects.filter(tv_show=tvshow).order_by('-created_at')[:5]
    is_in_watchlist = False
    
    if request.user.is_authenticated:
        is_in_watchlist = Watchlist.objects.filter(user=request.user, tv_show=tvshow).exists()
    
    # Group episodes by season
    seasons = {}
    for episode in episodes:
        season = episode.season_number
        if season not in seasons:
            seasons[season] = []
        seasons[season].append(episode)
    
    context = {
        'tvshow': tvshow,
        'seasons': seasons,
        'reviews': reviews,
        'is_in_watchlist': is_in_watchlist,
    }
    return render(request, 'content/tvshow_detail.html', context)


def episode_detail(request, episode_id):
    """Episode detail page"""
    episode = get_object_or_404(Episode, id=episode_id)
    tvshow = episode.tv_show
    
    # Get next and previous episodes
    next_episode = Episode.objects.filter(
        tv_show=tvshow,
        season_number=episode.season_number,
        episode_number__gt=episode.episode_number
    ).first()
    
    prev_episode = Episode.objects.filter(
        tv_show=tvshow,
        season_number=episode.season_number,
        episode_number__lt=episode.episode_number
    ).last()
    
    context = {
        'episode': episode,
        'tvshow': tvshow,
        'next_episode': next_episode,
        'prev_episode': prev_episode,
    }
    return render(request, 'content/episode_detail.html', context)


def search(request):
    """Search functionality"""
    query = request.GET.get('q', '')
    results = []
    
    if query:
        movies = Movie.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
        tvshows = TVShow.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
        results = {
            'movies': movies,
            'tvshows': tvshows,
        }
    
    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'content/search.html', context)


@login_required
def profile_select(request):
    """Show 'Who's Watching?' selection for the logged-in user."""
    profiles = Profile.objects.filter(user=request.user).order_by('created_at')
    # Provide a minimal set of genres for navbar (optional)
    genres = Genre.objects.all()[:8]
    return render(request, 'content/profile_select.html', {
        'profiles': profiles,
        'genres': genres,
    })


@login_required
def profile_use(request, profile_id):
    """Set the active profile in session and go to home."""
    profile = get_object_or_404(Profile, id=profile_id, user=request.user)
    request.session['active_profile_id'] = profile.id
    request.session['active_profile_name'] = profile.name
    return redirect('home')


def genre_view(request, genre_id):
    """View content by genre"""
    genre = get_object_or_404(Genre, id=genre_id)
    movies = Movie.objects.filter(genres=genre)
    tvshows = TVShow.objects.filter(genres=genre)
    
    context = {
        'genre': genre,
        'movies': movies,
        'tvshows': tvshows,
    }
    return render(request, 'content/genre_view.html', context)


@login_required
def watchlist_view(request):
    """User's watchlist"""
    watchlist_items = Watchlist.objects.filter(user=request.user).order_by('-added_at')
    
    context = {
        'watchlist_items': watchlist_items,
    }
    return render(request, 'content/watchlist.html', context)


@login_required
def add_to_watchlist(request):
    """Add item to watchlist"""
    if request.method == 'POST':
        content_type = request.POST.get('content_type')
        content_id = request.POST.get('content_id')
        active_profile_id = request.session.get('active_profile_id')
        if not active_profile_id:
            messages.error(request, "Select a profile first.")
            return redirect('profile_select')
        
        if content_type == 'movie':
            movie = get_object_or_404(Movie, id=content_id)
            ProfileWatchlist.objects.get_or_create(profile_id=active_profile_id, movie=movie)
        elif content_type == 'tvshow':
            tvshow = get_object_or_404(TVShow, id=content_id)
            ProfileWatchlist.objects.get_or_create(profile_id=active_profile_id, tv_show=tvshow)
        
        messages.success(request, 'Added to watchlist!')
    
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def remove_from_watchlist(request):
    """Remove item from watchlist"""
    if request.method == 'POST':
        content_type = request.POST.get('content_type')
        content_id = request.POST.get('content_id')
        active_profile_id = request.session.get('active_profile_id')
        if not active_profile_id:
            messages.error(request, "Select a profile first.")
            return redirect('profile_select')
        
        if content_type == 'movie':
            ProfileWatchlist.objects.filter(profile_id=active_profile_id, movie_id=content_id).delete()
        elif content_type == 'tvshow':
            ProfileWatchlist.objects.filter(profile_id=active_profile_id, tv_show_id=content_id).delete()
        
        messages.success(request, 'Removed from watchlist!')
    
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def add_review(request):
    """Add a review"""
    if request.method == 'POST':
        content_type = request.POST.get('content_type')
        content_id = request.POST.get('content_id')
        rating = int(request.POST.get('rating'))
        comment = request.POST.get('comment')
        
        if content_type == 'movie':
            movie = get_object_or_404(Movie, id=content_id)
            Review.objects.update_or_create(
                user=request.user,
                movie=movie,
                defaults={'rating': rating, 'comment': comment}
            )
        elif content_type == 'tvshow':
            tvshow = get_object_or_404(TVShow, id=content_id)
            Review.objects.update_or_create(
                user=request.user,
                tv_show=tvshow,
                defaults={'rating': rating, 'comment': comment}
            )
        
        messages.success(request, 'Review added successfully!')
    
    return redirect(request.META.get('HTTP_REFERER', '/'))
