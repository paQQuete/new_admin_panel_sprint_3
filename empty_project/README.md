## _Developed back-end service of online cinema for 3 sprints of the Yandex Practicum course_


This repository includes 5 services: 
- django as web backend, 
- postgres as database engine, 
- nginx as web server,
- elasticsearch as fulltext search, 
- etl as extract-transform-load service for continuous filling all data from database to search index
- extra service for transform SQLite DB to Postgres DB

## Running:
 - create file`empty_project/app/config/.env`
 - create file `empty_project/etl/.env`
 - create file `empty_project/pg_to_sql_loaddata/.env`
 - create file `empty_project/.env`
 - fill these files
```sh
cd empty_project && sudo docker-compose up --build
```

if needed to transfer data from sqlite to postgres:
```sh
sudo docker exec -it empty_project_sql2pg_1 sh 
```
in container shell: ```sh python load_data.py```


## empty_project/app/config/.env:
 - DB_NAME=`<Database name>`
 - DB_USER=`<Database user>`
 - DB_PASSWORD=`<Password of DB user>`
 - DB_HOST=`<Postgres host (hostname or IP address)>`
 - DB_PORT=`<Postgres port>`
 - DEBUG=`<Django debug mode (True or False)>`
 - SECRET_KEY=`<Django secret key>` you can generate this [HERE](https://djecrety.ir/)

## empty_project/etl/.env:
- DB_NAME=`<Database name>`
- DB_USER=`<Database user>`
- DB_PASSWORD=`<Password of DB user>`
- DB_HOST=`<Postgres host (hostname or IP address)>`
- DB_PORT=`<Postgres port>`
- ES_HOST=`<Elasticsearch host (hostname or IP address)>`
- ES_PORT=`<Elasticsearch port>`
- ELASTIC_URL=`<Elasticsearch full URL, (http://elasticsearch_host:port)>`
- LOOP_TIMEOUT=`<Main process timeout running (launch every ... seconds). It is recommended to set the value to more than
60 seconds>`

## empty_project/pg_to_sql_loaddata/.env:
 - DBNAME=`<Database name>`
 - DBUSER=`<Database user>`
 - PASSWORD=`<Password of DB user>`
 - HOST=`<Postgres host (hostname or IP address)>`
 - PORT=`<Postgres port>`

## empty_project/.env:
- POSTGRES_DB=`<Database name>`
- POSTGRES_USER=`<Database user>`
- POSTGRES_PASSWORD=`<Password of DB user>`
