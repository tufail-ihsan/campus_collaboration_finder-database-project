--  project Title
--  CAMPUS COLLABORATION FINDER
--  Team members: Tufail Ihsan · Muhammad Azam
--  Instructor: Dr. Musadaq Mansoor


CREATE DATABASE IF NOT EXISTS campus_collaboration_finder;

USE campus_collaboration_finder;


-- 1. STUDENTS
CREATE TABLE IF NOT EXISTS Students (
    student_id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    department VARCHAR(100) NOT NULL,
    semester INT NOT NULL CHECK (semester BETWEEN 1 AND 12),
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (student_id)
);

-- 2. SKILLS
CREATE TABLE IF NOT EXISTS Skills (
    skill_id     INT          NOT NULL AUTO_INCREMENT,
    skill_name   VARCHAR(100) NOT NULL UNIQUE,

    PRIMARY KEY (skill_id)
);


-- 3. STUDENT_SKILLS  (junction table)

CREATE TABLE IF NOT EXISTS Student_Skills (
    student_id   INT   NOT NULL,
    skill_id     INT   NOT NULL,

    PRIMARY KEY (student_id, skill_id),

    CONSTRAINT fk_ss_student
        FOREIGN KEY (student_id)
        REFERENCES Students (student_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_ss_skill
        FOREIGN KEY (skill_id)
        REFERENCES Skills (skill_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);


-- 4. PROJECTS

CREATE TABLE IF NOT EXISTS Projects (
    project_id INT NOT NULL AUTO_INCREMENT,
    owner_id INT NOT NULL,
    project_name VARCHAR(150) NOT NULL,
    description  TEXT,
    date_posted  DATE NOT NULL DEFAULT (CURRENT_DATE),

    PRIMARY KEY (project_id),

    CONSTRAINT fk_proj_owner
        FOREIGN KEY (owner_id)
        REFERENCES Students (student_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);


-- 5. PROJECT_SKILLS  (junction table)

CREATE TABLE IF NOT EXISTS Project_Skills (
    project_id INT NOT NULL,
    skill_id INT NOT NULL,

    PRIMARY KEY (project_id, skill_id),

    CONSTRAINT fk_ps_project
        FOREIGN KEY (project_id)
        REFERENCES Projects (project_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_ps_skill
        FOREIGN KEY (skill_id)
        REFERENCES Skills (skill_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);


-- 6. APPLICATIONS  (associative table)

CREATE TABLE IF NOT EXISTS Applications (
    application_id INT NOT NULL AUTO_INCREMENT,
    project_id INT NOT NULL,
    student_id INT NOT NULL,
    status ENUM('pending', 'approved', 'rejected') NOT NULL DEFAULT 'pending',
    date_applied DATE NOT NULL DEFAULT (CURRENT_DATE),

    PRIMARY KEY (application_id),

    -- A student can apply to the same project only once
    UNIQUE KEY uq_app (project_id, student_id),

    CONSTRAINT fk_app_project
        FOREIGN KEY (project_id)
        REFERENCES Projects (project_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_app_student
        FOREIGN KEY (student_id)
        REFERENCES Students (student_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);



-- SAMPLE DATA

-- Skills
INSERT INTO Skills (skill_name) VALUES
    ('Python'),
    ('Artificial Intelligence'),
    ('Web Development'),
    ('Machine Learning'),
    ('Data Science'),
    ('Java'),
    ('Database Design'),
    ('Mobile Development'),
    ('UI/UX Design'),
    ('Cloud Computing');


-- Students
INSERT INTO Students (name, email, department, semester, password) VALUES
    ('Tufail Ihsan',   'tufail@uni.edu',  'Computer Science',       6, 'hashed_pw_1'),
    ('Muhammad Azam',  'azam@uni.edu',    'Software Engineering',   5, 'hashed_pw_2'),
    ('Sara Khan',      'sara@uni.edu',    'Information Technology', 2, 'hashed_pw_3'),
    ('Ali Raza',       'ali@uni.edu',     'Computer Science',       8, 'hashed_pw_4'),
    ('Fatima Noor',    'fatima@uni.edu',  'Data Science',           3, 'hashed_pw_5'),
    ('Hassan Mehmood', 'hassan@uni.edu',  'Software Engineering',   7, 'hashed_pw_6');

-- Student_Skills
INSERT INTO Student_Skills (student_id, skill_id) VALUES
    -- Tufail: Python, AI, Web Dev
    (1, 1), (1, 2), (1, 3),
    -- Azam: Python, DB Design, Web Dev
    (2, 1), (2, 7), (2, 3),
    -- Sara: UI/UX, Web Dev
    (3, 9), (3, 3),
    -- Ali: ML, Python, Data Science
    (4, 4), (4, 1), (4, 5),
    -- Fatima: Data Science, Python
    (5, 5), (5, 1),
    -- Hassan: Java, Mobile Dev, Cloud
    (6, 6), (6, 8), (6, 10);

-- Projects

INSERT INTO Projects (owner_id, project_name, description, date_posted) VALUES
    (1, 'AI Study Buddy',
        'A chatbot that helps students revise course material using NLP.',
        '2026-01-10'),
    (2, 'Campus ERD Tool',
        'An online ERD builder tailored for university database courses.',
        '2026-01-15'),
    (4, 'Smart Attendance System',
        'Face-recognition based attendance tracker for classrooms.',
        '2026-01-20'),
    (6, 'Campus Event App',
        'A mobile app to discover and RSVP to campus events.',
        '2026-02-01');

-- Project_Skills  (required skills per project)
INSERT INTO Project_Skills (project_id, skill_id) VALUES
    -- AI Study Buddy: Python, AI, ML
    (1, 1), (1, 2), (1, 4),
    -- Campus ERD Tool: DB Design, Web Dev, Python
    (2, 7), (2, 3), (2, 1),
    -- Smart Attendance: Python, AI, ML
    (3, 1), (3, 2), (3, 4),
    -- Campus Event App: Mobile Dev, UI/UX, Cloud
    (4, 8), (4, 9), (4, 10);

-- Applications
INSERT INTO Applications (project_id, student_id, status, date_applied) VALUES
    (1, 3, 'pending',  '2026-01-12'),
    (1, 5, 'approved', '2026-01-13'),
    (2, 3, 'approved', '2026-01-17'),
    (3, 5, 'pending',  '2026-01-22'),
    (4, 1, 'rejected', '2026-02-03'),
    (4, 3, 'pending',  '2026-02-05');


-- USEFUL QUERIES

-- Q1: List all students with their skills

SELECT
    s.student_id,
    s.name,
    s.department,
    s.semester,
    sk.skill_name
FROM Students s
JOIN Student_Skills ss ON s.student_id = ss.student_id
JOIN Skills sk ON ss.skill_id  = sk.skill_id
ORDER BY s.name, sk.skill_name;


-- Q2: List all projects with their required skills and owner

SELECT
    p.project_id,
    p.project_name,
    s.name AS owner_name,
    sk.skill_name AS required_skill
FROM Projects p
JOIN Students s  ON p.owner_id = s.student_id
JOIN Project_Skills ps ON p.project_id = ps.project_id
JOIN Skills sk ON ps.skill_id  = sk.skill_id
ORDER BY p.project_name, sk.skill_name;

