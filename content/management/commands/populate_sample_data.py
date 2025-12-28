from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from content.models import Genre, Movie, TVShow, Episode, UserProfile
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Populate the database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create Genres
        genres_data = [
            {'name': 'Action', 'description': 'High-energy movies with lots of action sequences'},
            {'name': 'Comedy', 'description': 'Funny movies that will make you laugh'},
            {'name': 'Drama', 'description': 'Serious plot-driven stories'},
            {'name': 'Horror', 'description': 'Scary movies to give you chills'},
            {'name': 'Sci-Fi', 'description': 'Science fiction and futuristic stories'},
            {'name': 'Romance', 'description': 'Love stories and romantic comedies'},
            {'name': 'Thriller', 'description': 'Suspenseful and exciting movies'},
            {'name': 'Fantasy', 'description': 'Magical and fantastical stories'},
            {'name': 'Documentary', 'description': 'Non-fiction educational content'},
            {'name': 'Animation', 'description': 'Animated movies and series'},
        ]
        
        genres = []
        for genre_data in genres_data:
            genre, created = Genre.objects.get_or_create(
                name=genre_data['name'],
                defaults={'description': genre_data['description']}
            )
            genres.append(genre)
            if created:
                self.stdout.write(f'Created genre: {genre.name}')
        
        # Create Movies
        movies_data = [
            {
                'title': 'The Dark Knight',
                'description': 'When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.',
                'release_date': date(2008, 7, 18),
                'duration': 152,
                'rating': 9.0,
                'featured': True,
                'genres': ['Action', 'Drama', 'Thriller']
            },
            {
                'title': 'Inception',
                'description': 'A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.',
                'release_date': date(2010, 7, 16),
                'duration': 148,
                'rating': 8.8,
                'featured': True,
                'genres': ['Action', 'Sci-Fi', 'Thriller']
            },
            {
                'title': 'Pulp Fiction',
                'description': 'The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.',
                'release_date': date(1994, 10, 14),
                'duration': 154,
                'rating': 8.9,
                'featured': True,
                'genres': ['Crime', 'Drama']
            },
            {
                'title': 'The Shawshank Redemption',
                'description': 'Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.',
                'release_date': date(1994, 9, 23),
                'duration': 142,
                'rating': 9.3,
                'featured': True,
                'genres': ['Drama']
            },
            {
                'title': 'Interstellar',
                'description': 'A team of explorers travel through a wormhole in space in an attempt to ensure humanity\'s survival.',
                'release_date': date(2014, 11, 7),
                'duration': 169,
                'rating': 8.6,
                'featured': True,
                'genres': ['Drama', 'Sci-Fi']
            },
            {
                'title': 'The Matrix',
                'description': 'A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.',
                'release_date': date(1999, 3, 31),
                'duration': 136,
                'rating': 8.7,
                'featured': True,
                'genres': ['Action', 'Sci-Fi']
            }
        ]
        
        for movie_data in movies_data:
            movie, created = Movie.objects.get_or_create(
                title=movie_data['title'],
                defaults={
                    'description': movie_data['description'],
                    'release_date': movie_data['release_date'],
                    'duration': movie_data['duration'],
                    'rating': movie_data['rating'],
                    'featured': movie_data['featured']
                }
            )
            if created:
                # Add genres
                movie_genres = [g for g in genres if g.name in movie_data['genres']]
                movie.genres.set(movie_genres)
                self.stdout.write(f'Created movie: {movie.title}')
        
        # Create TV Shows
        tvshows_data = [
            {
                'title': 'Stranger Things',
                'description': 'When a young boy vanishes, a small town uncovers a mystery involving secret experiments, terrifying supernatural forces, and one strange little girl.',
                'release_date': date(2016, 7, 15),
                'rating': 8.7,
                'featured': True,
                'genres': ['Drama', 'Fantasy', 'Horror']
            },
            {
                'title': 'Breaking Bad',
                'description': 'A high school chemistry teacher diagnosed with inoperable lung cancer turns to manufacturing and selling methamphetamine in order to secure his family\'s future.',
                'release_date': date(2008, 1, 20),
                'rating': 9.5,
                'featured': True,
                'genres': ['Crime', 'Drama', 'Thriller']
            },
            {
                'title': 'The Crown',
                'description': 'Follows the political rivalries and romance of Queen Elizabeth II\'s reign and the events that shaped the second half of the 20th century.',
                'release_date': date(2016, 11, 4),
                'rating': 8.6,
                'featured': True,
                'genres': ['Biography', 'Drama', 'History']
            },
            {
                'title': 'Black Mirror',
                'description': 'An anthology series exploring a twisted, high-tech multiverse where humanity\'s greatest innovations and darkest instincts collide.',
                'release_date': date(2011, 12, 4),
                'rating': 8.8,
                'featured': True,
                'genres': ['Drama', 'Sci-Fi', 'Thriller']
            }
        ]
        
        tvshows = []
        for tvshow_data in tvshows_data:
            tvshow, created = TVShow.objects.get_or_create(
                title=tvshow_data['title'],
                defaults={
                    'description': tvshow_data['description'],
                    'release_date': tvshow_data['release_date'],
                    'rating': tvshow_data['rating'],
                    'featured': tvshow_data['featured']
                }
            )
            if created:
                # Add genres
                tvshow_genres = [g for g in genres if g.name in tvshow_data['genres']]
                tvshow.genres.set(tvshow_genres)
                tvshows.append(tvshow)
                self.stdout.write(f'Created TV show: {tvshow.title}')
        
        # Create Episodes for TV Shows
        episodes_data = [
            {
                'tvshow_title': 'Stranger Things',
                'episodes': [
                    {'season': 1, 'episode': 1, 'title': 'Chapter One: The Vanishing of Will Byers', 'description': 'On his way home from a friend\'s house, young Will sees something terrifying.', 'duration': 48},
                    {'season': 1, 'episode': 2, 'title': 'Chapter Two: The Weirdo on Maple Street', 'description': 'Lucas, Mike and Dustin try to talk to the girl they found in the woods.', 'duration': 56},
                    {'season': 1, 'episode': 3, 'title': 'Chapter Three: Holly, Jolly', 'description': 'An increasingly concerned Nancy looks for Barb and finds out what Jonathan\'s been up to.', 'duration': 51},
                    {'season': 2, 'episode': 1, 'title': 'Chapter Nine: The Gate', 'description': 'The gang discovers the truth about the Upside Down.', 'duration': 62},
                ]
            },
            {
                'tvshow_title': 'Breaking Bad',
                'episodes': [
                    {'season': 1, 'episode': 1, 'title': 'Pilot', 'description': 'A high school chemistry teacher discovers he has lung cancer.', 'duration': 58},
                    {'season': 1, 'episode': 2, 'title': 'Cat\'s in the Bag...', 'description': 'Walt and Jesse try to dispose of two bodies.', 'duration': 48},
                    {'season': 1, 'episode': 3, 'title': '...And the Bag\'s in the River', 'description': 'Walt and Jesse face the consequences of their actions.', 'duration': 50},
                ]
            }
        ]
        
        for show_data in episodes_data:
            try:
                tvshow = TVShow.objects.get(title=show_data['tvshow_title'])
                for ep_data in show_data['episodes']:
                    episode, created = Episode.objects.get_or_create(
                        tv_show=tvshow,
                        season_number=ep_data['season'],
                        episode_number=ep_data['episode'],
                        defaults={
                            'title': ep_data['title'],
                            'description': ep_data['description'],
                            'duration': ep_data['duration'],
                            'video_url': 'https://example.com/video',
                            'release_date': tvshow.release_date + timedelta(days=random.randint(0, 365))
                        }
                    )
                    if created:
                        self.stdout.write(f'Created episode: {episode.title}')
            except TVShow.DoesNotExist:
                continue
        
        # Create a test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write('Created test user: testuser (password: testpass123)')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated database with sample data!')
        )

