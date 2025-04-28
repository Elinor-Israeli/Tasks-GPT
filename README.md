```
docker run --name my-postgres -e POSTGRES_USER=elinor -e POSTGRES_PASSWORD=elinor123 -e POSTGRES_DB=ToDoApp_DB -p 5432:5432 -d postgres
docker build -t fastapi .
docker run -d -p 8000:8000 fastapi
```