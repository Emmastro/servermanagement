-- db_name, db_pwd and db_user will be replace by their actual values before dumping on mysql

CREATE DATABASE IF NOT EXISTS db_name;
CREATE USER IF NOT EXISTS 'db_user'@'localhost' IDENTIFIED BY 'db_pwd';
GRANT ALL PRIVILEGES ON `db_name`.* TO 'db_user'@'localhost';
FLUSH PRIVILEGES;
