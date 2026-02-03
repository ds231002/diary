function psql-diary {
    docker start diary-postgres | Out-Null
    docker exec -it diary-postgres psql -U diary -d diary
}

psql-diary