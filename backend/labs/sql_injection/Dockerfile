FROM mysql:5.7

ENV MYSQL_ROOT_PASSWORD=root
ENV MYSQL_DATABASE=vulnerable

COPY init.sql /docker-entrypoint-initdb.d/
