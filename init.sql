CREATE DATABASE IF NOT EXISTS cricket_db;
USE cricket_db;

CREATE TABLE IF NOT EXISTS cricket_scores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    team_1 VARCHAR(255),
    team_2 VARCHAR(255),
    match_result TEXT,
    timestamp DOUBLE
);
