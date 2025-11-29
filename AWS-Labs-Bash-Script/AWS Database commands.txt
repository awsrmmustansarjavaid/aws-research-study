
# update packages
 sudo apt update && sudo apt upgrade -y

or 

sudo dnf update -y

# install mysql
 sudo apt install mariadb-client
or 

sudo dnf install mariadb105 -y

# test
 mysql --version

# retrieved endpoint, username, and password to connect
 mysql -h <RDS_Endpoint> -P 3306 -u <RDS_Username> -p

# after connect show db lists
 SHOW DATABASES;

# create new database
 CREATE DATABASE dbname;

# switch to your db
 USE dbname;

# create user table
 CREATE TABLE users (
 id INT AUTO_INCREMENT PRIMARY KEY,
 name VARCHAR(100) NOT NULL,
 email VARCHAR(100) UNIQUE NOT NULL
 );

# insert sample data
 INSERT INTO users (name, email) 
VALUES 
('Alamgir Hosen', 'alamgir@example.com'),
 ('Abir Ahmed', 'abir@example.com');

 INSERT INTO users (name, email) 
VALUES 
('ali khan', 'alikhan@example.com'),
 ('usman Ahmed', 'usmana@example.com');

 INSERT INTO users (name, email) 
VALUES 
('Alamgir j', 'alwmgir@example.com'),
 ('Abir Ahmaed', 'awwir@example.com');




# see table lists
 SHOW TABLES;

# show data from specific table
 SELECT * FROM users;

# leave from db
 Exit;



