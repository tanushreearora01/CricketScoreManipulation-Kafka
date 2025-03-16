CREATE DATABASE IF NOT EXISTS cricket_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE cricket_db;

CREATE TABLE IF NOT EXISTS cricket_scores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    team_1 VARCHAR(255),
    team_2 VARCHAR(255),
    match_result TEXT,
    timestamp DOUBLE
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;