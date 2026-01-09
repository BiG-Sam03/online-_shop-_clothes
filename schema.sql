-- Online Shop (Clothes) - MySQL schema
CREATE DATABASE IF NOT EXISTS online_shop_clothes CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE online_shop_clothes;

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(120) NOT NULL,
  email VARCHAR(190) NOT NULL UNIQUE,
  password_hash VARCHAR(500) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
