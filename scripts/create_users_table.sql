-- Script de création de la table users pour l'authentification

-- Créer la base de données (si elle n'existe pas)
CREATE DATABASE IF NOT EXISTS rag_legal_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE rag_legal_db;

-- Supprimer la table si elle existe (pour réinitialisation)
-- DROP TABLE IF EXISTS users;

-- Créer la table users
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('guest', 'employee', 'admin') NOT NULL DEFAULT 'guest',
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_username (username),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Afficher la structure de la table
DESCRIBE users;
