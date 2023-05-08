conn = new Mongo();

const name_db = process.env.MONGO_DB;
db = conn.getDB(name_db);

// db.createCollection("to_be_removed");
db.createCollection("commands");

// db.to_be_removed.insertOne(
//     {text: ["скажи", "расскажи", "покажи", "сколько", "произнеси", "произнеси"]},
// );
db.commands.insertOne(
    {
        author: ["кто автор фильма", "автор фильма", "автор"],
        how_films: ["сколько фильмов выпустил автор", "сколько фильмов выпустил",
            "сколько фильмов создал автор", "сколько фильмов создал"],
        time_film: ["сколько длится фильм", "сколько по времени идет фильм", "сколько часов идет фильм",
            "как долго идет фильм", "сколько по времени длится фильм", "как долго длится фильм"]
    }
);

conn.close();

