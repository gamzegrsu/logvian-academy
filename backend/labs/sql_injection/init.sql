CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(100),
  password VARCHAR(100)
);

INSERT INTO users (username, password) VALUES
('admin', 'notsecure'),
('guest', 'guest123');

CREATE TABLE secrets (
  id INT AUTO_INCREMENT PRIMARY KEY,
  flag VARCHAR(255)
);

INSERT INTO secrets (flag) VALUES ("FLAG{sql_injection_success}");
