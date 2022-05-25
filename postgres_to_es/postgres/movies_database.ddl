CREATE SCHEMA IF NOT EXISTS content;
ALTER ROLE app SET search_path TO content,public;

CREATE TABLE IF NOT EXISTS content.film_work (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    description TEXT,
    creation_date DATE,
    rating FLOAT,
    type TEXT NOT NULL,
    created timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    modified timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS content.person (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name TEXT NOT NULL,
    created timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    modified timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS content.person_film_work (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    film_work_id uuid NOT NULL,
    person_id uuid NOT NULL,
    role TEXT NOT NULL,
    created timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS content.genre (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name varchar (20),
    description TEXT,
    created timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    modified timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS content.genre_film_work (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    genre_id uuid NOT NULL,
    film_work_id uuid NOT NULL,
    created timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS film_work_creation_date_idx ON content.film_work(creation_date);
CREATE UNIQUE INDEX IF NOT EXISTS film_work_person_idx ON content.person_film_work (id,film_work_id, person_id);

-- создается таблица в которою будут сбрасываться данные об уделенных записей из таблиц
create table if not exists content.del_item(
    id uuid not null default gen_random_uuid(),
    table_name text not null,
    field_id uuid not null,
    created timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

-- создаем функцию которая возвращает массив жанров по id фильма
CREATE OR replace function get_genre_by_id_film (uuid) RETURNS SETOF character array as
$$
select
array_agg(distinct g."name"  )
from "content".film_work fw2
left join "content".genre_film_work gfw on gfw.film_work_id = fw2.id
left join "content".genre g on g.id =gfw.genre_id
where $1=fw2.id
group by fw2.id;
$$
LANGUAGE sql;

-- создаем функцию которая возвращает массив персон по id фильма и их роли ('actor')
CREATE OR replace function get_person_by_id_film (uuid, character) RETURNS SETOF character array as
$$
select
coalesce(array_agg(distinct p.full_name) filter (where pfw."role" = $2), '{}')
from "content".film_work fw2
left JOIN content.person_film_work pfw ON pfw.film_work_id = fw2.id
left JOIN content.person p ON p.id = pfw.person_id
where $1=fw2.id
group by fw2.id;
$$
LANGUAGE sql;

-- создаем функцию которая возвращает JSON персон по id фильма и их роли ('actor')
CREATE OR replace function get_person_by_id_film_from_JSON (uuid, character) RETURNS SETOF json  as
$$
select
coalesce(json_agg(distinct jsonb_build_object('id', p.id, 'name', p.full_name)) filter (where pfw."role" = $2), '[]') as actors
from "content".film_work fw2
left JOIN content.person_film_work pfw ON pfw.film_work_id = fw2.id
left JOIN content.person p ON p.id = pfw.person_id
where $1=fw2.id
group by fw2.id;

$$
LANGUAGE sql;

create OR replace function trigger_before_del () returns trigger as
$$
begin
	insert into del_item (table_name, field_id) values (TG_RELNAME, old.id);
	case TG_RELNAME
		when 'genre' then
			update "content".film_work  as fw set modified = default
			from "content".genre_film_work as gfw , "content".genre as g
			where gfw.genre_id = g.id  and gfw.film_work_id =fw.id and g."name" = old."name";
		when 'person' then
			update "content".film_work  as fw set modified = default
			from "content".person_film_work as pfw , "content".person as p
			where pfw.person_id = p.id  and pfw.film_work_id =fw.id and p.full_name  = old.full_name;
		else
			select table_name
			from information_schema.columns
			where table_schema='public';
	end case;
	return old;
end;
$$
LANGUAGE plpgsql;

-- Создаем триггеры на удаление записей, если записи удаляются из основных таблиц
-- мы информацию об удаленных полях заносим в таблицу  del_item

create trigger tr_genre_before_del
before delete on content.genre for each row
execute procedure trigger_before_del();

create trigger tr_person_before_del
before delete on content.person for each row
execute procedure trigger_before_del();

create trigger tr_content_film_work_before_del
before delete on content.film_work for each row
execute procedure trigger_before_del();


