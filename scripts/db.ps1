function psql-diary {
    docker start diary-postgres | Out-Null
    docker exec -it diary-postgres psql -Udiary -d diary
}

psql-diary