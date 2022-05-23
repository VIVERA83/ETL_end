# ETL

___
__Привет__ не забудь создать .env,

* 1 __запуск через docker__
  ```
     docker-compose up --build
  ```
  Возможные сложности:
    * убедись что название контейнеров не пересекаются с уже имеющимися названиями
        * redis
        * elasticsearch
        * postgres
        * sqlete_to_postgres
        * postgres_to_es
          если названия пересикаются переменуй их в  [Docker-compose.yaml](Docker-compose.yaml)

* 2 - __запуск "ручками", локально__:
    1) Сначало необходимо локально запустить:
        1) [Redis](https://redis.io/) 
       ```docker run -d --name redis -p 6379:6379 redis```
        2) [Elasticsearch](https://www.elastic.co/elasticsearch/) версия 7.17.1
        ```docker run -d --name elastic -p 9200:9200 -e "discovery.type=single-node" elasticsearch:7.17.1```
        3) [Postgres](https://www.postgresql.org/) версия 13
    2) Запускаем:
       [sqlete_to_postgres/run.py](sqlete_to_postgres/run.py)
        Данная штука в первую очередь создает [необходимые таблицы и записи](sqlete_to_postgres/app/movies_database.ddl) в postgres, далее скопирует sqllite бд в postgres
    3) Запускаем: [postgres_to_es/run.py](postgres_to_es/run.py) 
        
После запустится ETL, 
    на текущий момент ELT умеет:
* Переносить postgres в elastic
* Отслеживать изменения в postgres таблицах и отправлять их в elastic
  Пример, если в какой не будь жанр, скажем с 'Drama' на 'Драма' то все документы в индексе movies, в которых был упомянут данный жанр будут обновлены.    
* Отслеживать удаление полей из postgres и обновлять затронутые данными изменениями записи в elastic
* Умеет дожидаться восстановления связи с любой из используемых баз. При возникновении сбоя во время передачи сохраняет текущие состояние в redis.
* В случаии если redis пуст, начнется полный перенос данных в elastic
* id записей в postgres =  id записи в elastic