-- Drop the user if it already exists
DROP USER IF EXISTS 'auth_user'@'localhost';

-- Create the new user with a password
CREATE USER 'auth_user'@'localhost' IDENTIFIED BY 'admin';

-- Create the database
CREATE DATABASE IF NOT EXISTS auth;

-- Grant privileges on the auth database to the user
GRANT SELECT, INSERT, UPDATE, DELETE, LOCK TABLES ON auth.* TO 'auth_user'@'localhost';

-- Apply changes
FLUSH PRIVILEGES;

-- Use the database
USE auth;

-- Create the users table
CREATE TABLE IF NOT EXISTS users (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

-- Insert a sample user into the table
INSERT INTO users (email, password) VALUES ('nishatoma@gmail.com', 'admin');
