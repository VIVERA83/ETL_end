# get_genre_by_id_film (fw.id) ручками написанная функция которая заводится в БД при создании таблиц
# лежит в \sqlete_to_postgres\app\movies_database.ddl

SQL_MOVIES = {"select": """
               SELECT
               fw.id,
               fw.rating as imdb_rating,
               get_genre_by_id_film (fw.id) as genre,
               fw.title,
               coalesce(fw.description, '') as description,
               get_person_by_id_film (fw.id, 'director') as director,
               get_person_by_id_film (fw.id, 'actor') as actors_names,
               get_person_by_id_film (fw.id, 'writer') as writers_names,
               get_person_by_id_film_from_JSON(fw.id,'actor') as actors,
               get_person_by_id_film_from_JSON(fw.id,'writer') as writers
               FROM content.film_work fw
               LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
               LEFT JOIN content.person p ON p.id = pfw.person_id
               LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
               LEFT JOIN content.genre g ON g.id = gfw.genre_id
            """,
              "where": "fw.modified > '{date}' or g.modified > '{date}' or p.modified > '{date}'",
              "group_field": "fw.id",
              "order_field": "fw.modified",
              "index": "movies",
              "prescription": "select",
              }

SQL_PERSON = {"select": """select p.id, p.full_name from "content".person p """,
              "where": "p.modified > '{date}' ",
              "group_field": "p.id",
              "order_field": "p.modified",
              "index": "person",
              "prescription": "select",
              }

SQL_GENRE = {"select": """select g.id , g."name" , g.description  from genre g """,
             "where": "g.modified > '{date}' ",
             "group_field": "g.id",
             "order_field": "g.modified",
             "index": "genre",
             "prescription": "select",
             }

SQL_DELETE = {
             "select": """select di.id, di.field_id, di.table_name, di.created from "content".del_item di """,
             "where": "di.created > '{date}' ",
             "group_field": "",
             "order_field": "di.created",
             "index": "del_item",
             "prescription": "delete",
             }
