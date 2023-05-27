import pytest


@pytest.mark.parametrize(
    'user_query_text, actual_command',
    [
        ('кто автор фильма матрица', 'author'),
        ('подскажи кто создатель фильма матрица', 'author'),
        ('фильмы с актером Тратата', 'actor'),
        ('топ фильмы с участием Тратата', 'actor'),
        ('сколько фильмов снял режиссер Сталоне', 'how_many_films'),
        ('какое количество фильмов снял режиссер СТалоне', 'how_many_films'),
        ('сколько длится фильм тратара', 'time_film'),
        ('сколько идет фильм тратата', 'time_film'),
        ('топ фильмов', 'top_films'),
        ('топ фильмов в жанре комедия', 'top_films_genre'),
        ('в каких жанрах снят фильм матрица', 'film_genre'),
        ('какой жанр у фильма матрица', 'film_genre'),
        ('топ актер в мире', 'top_actor'),
        ('о чем фильм матрица', 'film_about'),
        ('расскажи о чем фильм матрица', 'film_about'),
        ('в каком году вышел фильм матрица', 'film_year'),
        ('год создания фильма матрица', 'film_year'),
        ('какой рейтинг у фильма матрица', 'film_rating'),
        ('какие отзывы о фильме матрица', 'film_rating'),
    ],
)
@pytest.mark.asyncio
async def test_recognize_command(command_handler, user_query_text, actual_command):
    user_query_object = await command_handler.handle_user_query(user_query_text)
    print(user_query_text, user_query_object.final_cmd)
    assert user_query_object.final_cmd == actual_command
