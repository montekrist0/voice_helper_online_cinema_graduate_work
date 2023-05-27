conn = new Mongo();

const name_db = process.env.MONGO_DB;
db = conn.getDB(name_db);

db.createCollection("to_be_removed");
db.createCollection("commands");

db.to_be_removed.insertOne(
    {
        text: ["мне", "каком", "каких", "какой",
            "каком", "какое", "скажи", "расскажи",
            "покажи", "сколько", "произнеси", "произнеси",
            "кто", "как", "много", "количество", "назови", "где", "*",
            "в", "а", "бы", "подскажи", "расскажи", "у", "c", "какого", "о", "по"
        ]
    },
);

db.commands.insertOne(
    {
        author: ["автор фильма", "автор", "фильм автор", "автора", "авторы",
            "создатель фильма", "создал"],

        actor: ["фильме играл", "актер фильма", "актёр фильма", "актриса играла",
            "фильме играла", "актриса фильма", "фильмах играл", "фильмах играла",
            "актёр снимается в фильме", "актриса снимается в фильме", "актер снимается в фильме",
            "играл актер", "играла актриса", "играл актёр", "фильме играл актёр",
            "фильме играла актриса", "фильме снимался", "сериале снимался", "фильмах снимался",
            "сериалах снимался", "фильмы с участием", "сериалы с участием"
        ],

        how_many_films: ["фильмов выпустил автор", "фильмов выпустил режиссер", "фильмов выпустил", "выпустил",
            "создал", "выпустил фильм", "фильмов создал автор", "фильмов создал", "фильмов снял"],

        time_film: ["длится фильм", "длится", "времени идет фильм", "времени идёт фильм", "времени идет",
            "времени идёт", "часов идет фильм", "часов идёт фильм", "часов идёт", "часов идет", "минут идет фильм",
            "минут идёт фильм", "минут идет", "минут идёт", "долго идет", "долго идёт",
            "долго идет фильм", "времени длится фильм", "долго длится фильм", "минут идет", "идет фильм",
            "фильм идет"],

        top_films: ["топ десять фильмов", "топ 10 фильмов", "топ десять фильмов", "кинохиты",
            "лучшие фильмы", "топ фильмы", "топ фильмов"],

        top_films_genre: ["топ десять фильмов жанре", "топ 10 фильмов жанре",
            "топ десять жанре", "топ 10 жанре", "топ жанре"],

        film_genre: ["жанре снят фильм", "жанр фильма", "жанре снят фильм", "жанре фильм", "жанре"],

        top_actor: ["самый популярный актер", "лучший актер", "топ актер", "самый популярный актёр", "лучший актёр",
            "топ актёр", "популярный актёр"],

        film_about: ["про фильм", "про что сериал", "про что фильм" , "чем фильм", "чём фильм", "чем сериал", "чём сериал",
            "сюжет фильма", "сюжет сериала", "описание фильма", "описание сериала", "чем суть сериала",
            "чем суть фильма"],

        film_year: ["год выпуска", "дата создания", "году вышел", "год создания", "дата выхода прокат",
            "вышел фильм", "вышел фильм", "года выпуска", "какой год выпуска",
            "сколько лет фильму", "сколько лет сериалу"],

        film_rating: ["рейтинг фильма", "рейтинг сериала", "рейтинг", "рейтинг",
            "отзывы фильма", "отзывы сериала", "оценка фильма"]

    }
);

conn.close();

