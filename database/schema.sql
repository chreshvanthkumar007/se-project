-- =======================================================
-- AI Student Feedback Analyzer - Database Schema
-- Database: ai_student_feedback
-- Target RDBMS: MySQL 8.0+
-- =======================================================

CREATE DATABASE IF NOT EXISTS ai_student_feedback
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE ai_student_feedback;

-- Drop tables in reverse dependency order if resetting
DROP TABLE IF EXISTS feedback_analysis;
DROP TABLE IF EXISTS feedback;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS users;

-- -------------------------------------------------------
-- Table: users
-- Stores both Administrators and Students
-- -------------------------------------------------------
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(50) UNIQUE NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'student') NOT NULL DEFAULT 'student',
    department VARCHAR(100) DEFAULT 'Computer Science & Engineering',
    year INT DEFAULT 3,
    semester INT DEFAULT 5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_role (role),
    INDEX idx_user_email (email),
    INDEX idx_user_student_id (student_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------
-- Table: categories
-- Stores feedback target domains
-- -------------------------------------------------------
CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------
-- Table: feedback
-- Stores student feedback submissions and core sentiment
-- -------------------------------------------------------
CREATE TABLE feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    category VARCHAR(100) NOT NULL,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    feedback_text TEXT NOT NULL,
    sentiment VARCHAR(20) NOT NULL DEFAULT 'Neutral',
    sentiment_score DECIMAL(4,2) NOT NULL DEFAULT 0.00,
    status ENUM('Pending', 'Analyzed', 'Reviewed') NOT NULL DEFAULT 'Analyzed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_feedback_student FOREIGN KEY (student_id)
        REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_feedback_student (student_id),
    INDEX idx_feedback_category (category),
    INDEX idx_feedback_sentiment (sentiment),
    INDEX idx_feedback_rating (rating),
    INDEX idx_feedback_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------
-- Table: feedback_analysis
-- Stores granular AI insights for each feedback
-- -------------------------------------------------------
CREATE TABLE feedback_analysis (
    id INT AUTO_INCREMENT PRIMARY KEY,
    feedback_id INT NOT NULL UNIQUE,
    keywords TEXT,
    topics TEXT,
    strengths TEXT,
    problems TEXT,
    recommendations TEXT,
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_analysis_feedback FOREIGN KEY (feedback_id)
        REFERENCES feedback(id) ON DELETE CASCADE,
    INDEX idx_analysis_feedback (feedback_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
