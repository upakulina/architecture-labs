DROP TABLE IF EXISTS grades;
DROP TABLE IF EXISTS gradebooks;

CREATE TABLE gradebooks (
    id SERIAL PRIMARY KEY,
    course_name TEXT NOT NULL,
    group_name TEXT NOT NULL,
    semester TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open'
);

CREATE TABLE grades (
    id SERIAL PRIMARY KEY,
    gradebook_id INT NOT NULL REFERENCES gradebooks(id) ON DELETE CASCADE,
    student_name TEXT NOT NULL,
    control_name TEXT NOT NULL,
    score NUMERIC(5,2) NOT NULL CHECK (score >= 0 AND score <= 10)
);

INSERT INTO gradebooks (course_name, group_name, semester, status)
VALUES
('Архитектура программных систем', 'РИС-22-3', '2025/2026 осень', 'open'),
('Базы данных', 'РИС-22-3', '2025/2026 осень', 'open');

INSERT INTO grades (gradebook_id, student_name, control_name, score)
VALUES
(1, 'Иванов Иван', 'Лабораторная работа 1', 8),
(1, 'Петрова Анна', 'Лабораторная работа 1', 9),
(2, 'Иванов Иван', 'Контрольная работа 1', 7);