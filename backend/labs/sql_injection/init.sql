CREATE DATABASE IF NOT EXISTS vulnerable;
USE vulnerable;
CREATE TABLE IF NOT EXISTS secrets (
    id INT PRIMARY KEY AUTO_INCREMENT,
    flag VARCHAR(255)
);

INSERT INTO secrets(flag) VALUES ("FLAG{sql_master}");
