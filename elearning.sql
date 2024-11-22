DROP DATABASE IF EXISTS elearning_platform;
CREATE DATABASE elearning_platform;
USE elearning_platform;

-- Create User table
CREATE TABLE user (
    user_id INT NOT NULL AUTO_INCREMENT,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    age INT,
    address VARCHAR(255),
    phone_number VARCHAR(15),
    profession VARCHAR(100),
    PRIMARY KEY (user_id),
    UNIQUE KEY (username)
);

-- Create Course table
CREATE TABLE course (
    course_id INT NOT NULL AUTO_INCREMENT,
    course_name VARCHAR(255) NOT NULL,
    PRIMARY KEY (course_id)
);

-- Create Assessment table
CREATE TABLE assessment (
    course_name VARCHAR(255) NOT NULL,
    question_id VARCHAR(50) NOT NULL,
    correct_answer VARCHAR(255) NOT NULL,
    PRIMARY KEY (question_id)
);

-- Create Contact Us table
CREATE TABLE contactus (
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    PRIMARY KEY (id)
);

-- Create Enrollment table
CREATE TABLE enrollment (
    enrollment_id INT NOT NULL AUTO_INCREMENT,
    user_id INT,
    username VARCHAR(255) NOT NULL,
    course_name VARCHAR(255) NOT NULL,
    course_id INT,
    enrollment_date DATE NOT NULL,
    completion_status VARCHAR(50) NOT NULL,
    PRIMARY KEY (enrollment_id),
    FOREIGN KEY (user_id) REFERENCES user(user_id),
    FOREIGN KEY (course_id) REFERENCES course(course_id)
);

-- Create Certificate table
CREATE TABLE certificate (
    certificate_id INT NOT NULL AUTO_INCREMENT,
    user_id INT,
    course_name VARCHAR(255) NOT NULL,
    marks INT,
    username VARCHAR(255) NOT NULL,
    assessment_date DATE,
    course_id INT,
    PRIMARY KEY (certificate_id),
    FOREIGN KEY (user_id) REFERENCES user(user_id),
    FOREIGN KEY (course_id) REFERENCES course(course_id)
);

-- Create trigger to automatically set user_id and course_id in enrollment table
DELIMITER //
CREATE TRIGGER before_enrollment_insert
BEFORE INSERT ON enrollment
FOR EACH ROW
BEGIN
    -- Set the user_id based on username
    SET NEW.user_id = (
        SELECT user_id 
        FROM user 
        WHERE username = NEW.username
    );
    
    -- Set the course_id based on course_name
    SET NEW.course_id = (
        SELECT course_id 
        FROM course 
        WHERE course_name = NEW.course_name
    );
END;//
DELIMITER ;

-- Create trigger to automatically set user_id and course_id in certificate table
DELIMITER //
CREATE TRIGGER before_certificate_insert
BEFORE INSERT ON certificate
FOR EACH ROW
BEGIN
    -- Set the user_id based on username
    SET NEW.user_id = (
        SELECT user_id 
        FROM user 
        WHERE username = NEW.username
    );
    
    -- Set the course_id based on course_name
    SET NEW.course_id = (
        SELECT course_id 
        FROM course 
        WHERE course_name = NEW.course_name
    );
END;//
DELIMITER ;

-- Function to check if a user is enrolled in a course
DELIMITER //
CREATE FUNCTION check_course_enrollment(p_username VARCHAR(255), p_course_name VARCHAR(255))
RETURNS BOOLEAN
DETERMINISTIC
BEGIN
    DECLARE enrollment_exists INT;
    
    SELECT COUNT(*) INTO enrollment_exists
    FROM enrollment
    WHERE username = p_username 
    AND course_name = p_course_name;
    
    IF enrollment_exists > 0 THEN
        RETURN TRUE;
    ELSE
        RETURN FALSE;
    END IF;
END;//
DELIMITER ;

-- Insert courses
INSERT INTO course (course_name) VALUES
('Artificial Intelligence Basics'),
('Cloud Computing Essentials'),
('Data Science with R'),
('Machine Learning'),
('Python Programming'),
('Web Development');

-- Insert assessment data
INSERT INTO assessment (course_name, question_id, correct_answer) VALUES
('Artificial Intelligence Basics', 'ai_q1', 'To mimic human brain functions'),
('Artificial Intelligence Basics', 'ai_q2', 'To enable machines to interpret and generate human language'),
('Artificial Intelligence Basics', 'ai_q3', 'To interpret and analyze visual data from the world'),
('Artificial Intelligence Basics', 'ai_q4', 'Computer Vision'),
('Cloud Computing Essentials', 'cc_q1', 'Scalability and flexibility'),
('Cloud Computing Essentials', 'cc_q2', 'AWS, Google Cloud, Microsoft Azure'),
('Cloud Computing Essentials', 'cc_q3', 'On-demand resources'),
('Cloud Computing Essentials', 'cc_q4', 'Cloud services provided over the internet'),
('Data Science with R', 'ds_q1', 'dplyr'),
('Data Science with R', 'ds_q2', 'ggplot2'),
('Data Science with R', 'ds_q3', 'randomForest'),
('Data Science with R', 'ds_q4', 'Data manipulation'),
('Machine Learning', 'ml_q1', 'Learning from labeled data'),
('Machine Learning', 'ml_q2', 'Linear Regression'),
('Machine Learning', 'ml_q3', 'Finding patterns in unlabeled data'),
('Machine Learning', 'ml_q4', 'Cross-validation'),
('Python Programming', 'py_q1', 'Indentation'),
('Python Programming', 'py_q2', 'def function_name():'),
('Python Programming', 'py_q3', 'Storing multiple items'),
('Python Programming', 'py_q4', 'Exception handling'),
('Web Development', 'wd_q1', 'To structure and organize content'),
('Web Development', 'wd_q2', 'color'),
('Web Development', 'wd_q3', 'To create dynamic and interactive content'),
('Web Development', 'wd_q4', 'Backend programming languages like PHP, Node.js');