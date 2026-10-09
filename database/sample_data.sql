-- =======================================================
-- AI Student Feedback Analyzer - Sample Data
-- Database: ai_student_feedback
-- =======================================================

USE ai_student_feedback;

-- -------------------------------------------------------
-- Seed Categories
-- -------------------------------------------------------
INSERT INTO categories (category_name, description) VALUES
('Faculty', 'Feedback related to faculty behavior, guidance, and mentorship.'),
('Course', 'Curriculum relevance, syllabus pacing, and academic content.'),
('Teaching', 'Teaching methodologies, pedagogy, and classroom explanations.'),
('Laboratory', 'Lab equipment, hardware, practical experiments, and technical staff.'),
('Infrastructure', 'Classrooms, projectors, air conditioning, seating, and power outlets.'),
('Library', 'Availability of books, digital journals, study spaces, and reading halls.'),
('Campus', 'Campus cleanliness, cafeteria, green spaces, sports facilities, and parking.'),
('Student Services', 'Administrative desk, placement cell, scholarship help, and grievance cell.'),
('Overall Experience', 'General college atmosphere, institutional culture, and student life.')
ON DUPLICATE KEY UPDATE description=VALUES(description);

-- -------------------------------------------------------
-- Seed Users (Admin & Students)
-- Passwords:
-- admin@college.edu    => admin123
-- student emails       => student123
-- -------------------------------------------------------
INSERT INTO users (student_id, name, email, password_hash, role, department, year, semester) VALUES
(NULL, 'Dean Dr. Ronald Vance', 'admin@college.edu', 'scrypt:32768:8:1$B0UAVvY4h7y9KcVb$8b465fe28a18d3ea7072b8e90fb5760bc19865ced9b20c0d93d918c73d68e6b867b724464b95bc5fba236fa5b5c3827d1a8e8488b01a19222a8864d16ff2b562', 'admin', 'Academic Administration', 0, 0),
('STU202401', 'Alex Turner', 'alex.turner@college.edu', 'scrypt:32768:8:1$ctZJm1AG6m2Dx96l$987895c2006d9dd7551d592d6809eeb0b01bfa5285b9da149e4f834d4b75fa049a515539c9276b8f6dba1592033d72a3919005449328b72aa5af4fd67a3004ef', 'student', 'Computer Science & Engineering', 3, 5),
('STU202402', 'Priya Sharma', 'priya.sharma@college.edu', 'scrypt:32768:8:1$ctZJm1AG6m2Dx96l$987895c2006d9dd7551d592d6809eeb0b01bfa5285b9da149e4f834d4b75fa049a515539c9276b8f6dba1592033d72a3919005449328b72aa5af4fd67a3004ef', 'student', 'Computer Science & Engineering', 3, 5),
('STU202403', 'Rahul Verma', 'rahul.verma@college.edu', 'scrypt:32768:8:1$ctZJm1AG6m2Dx96l$987895c2006d9dd7551d592d6809eeb0b01bfa5285b9da149e4f834d4b75fa049a515539c9276b8f6dba1592033d72a3919005449328b72aa5af4fd67a3004ef', 'student', 'Information Technology', 2, 3),
('STU202404', 'Ananya Sen', 'ananya.sen@college.edu', 'scrypt:32768:8:1$ctZJm1AG6m2Dx96l$987895c2006d9dd7551d592d6809eeb0b01bfa5285b9da149e4f834d4b75fa049a515539c9276b8f6dba1592033d72a3919005449328b72aa5af4fd67a3004ef', 'student', 'Electronics & Communication', 4, 7),
('STU202405', 'David Miller', 'david.miller@college.edu', 'scrypt:32768:8:1$ctZJm1AG6m2Dx96l$987895c2006d9dd7551d592d6809eeb0b01bfa5285b9da149e4f834d4b75fa049a515539c9276b8f6dba1592033d72a3919005449328b72aa5af4fd67a3004ef', 'student', 'Mechanical Engineering', 2, 4),
('STU202406', 'Sneha Patel', 'sneha.patel@college.edu', 'scrypt:32768:8:1$ctZJm1AG6m2Dx96l$987895c2006d9dd7551d592d6809eeb0b01bfa5285b9da149e4f834d4b75fa049a515539c9276b8f6dba1592033d72a3919005449328b72aa5af4fd67a3004ef', 'student', 'Civil Engineering', 3, 6),
('STU202407', 'Arjun Nair', 'arjun.nair@college.edu', 'scrypt:32768:8:1$ctZJm1AG6m2Dx96l$987895c2006d9dd7551d592d6809eeb0b01bfa5285b9da149e4f834d4b75fa049a515539c9276b8f6dba1592033d72a3919005449328b72aa5af4fd67a3004ef', 'student', 'Computer Science & Engineering', 4, 8),
('STU202408', 'Kavita Reddy', 'kavita.reddy@college.edu', 'scrypt:32768:8:1$ctZJm1AG6m2Dx96l$987895c2006d9dd7551d592d6809eeb0b01bfa5285b9da149e4f834d4b75fa049a515539c9276b8f6dba1592033d72a3919005449328b72aa5af4fd67a3004ef', 'student', 'Information Technology', 1, 2);

-- -------------------------------------------------------
-- Seed Feedback Entries
-- -------------------------------------------------------
INSERT INTO feedback (id, student_id, category, rating, feedback_text, sentiment, sentiment_score, status, created_at) VALUES
(1, 2, 'Faculty', 5, 'The faculty explains complex algorithms with great clarity and provides practical code examples in every lecture. Always available during office hours.', 'Positive', 0.88, 'Analyzed', DATE_SUB(NOW(), INTERVAL 14 DAY)),
(2, 3, 'Laboratory', 2, 'The faculty explains concepts clearly, but the laboratory equipment is outdated and needs improvement. Half of the oscilloscope machines in lab 3 do not work.', 'Mixed', -0.15, 'Analyzed', DATE_SUB(NOW(), INTERVAL 13 DAY)),
(3, 4, 'Teaching', 4, 'Interactive teaching style with real-world case studies made Operating Systems very engaging. Would appreciate more hands-on quiz sessions.', 'Positive', 0.74, 'Analyzed', DATE_SUB(NOW(), INTERVAL 12 DAY)),
(4, 5, 'Infrastructure', 1, 'The air conditioning in lecture hall 204 has been broken for three weeks and the ceiling projector blinks constantly during seminars.', 'Negative', -0.79, 'Analyzed', DATE_SUB(NOW(), INTERVAL 11 DAY)),
(5, 6, 'Library', 5, 'Exceptional collection of research journals and IEEE papers. The silent reading room is very comfortable and perfect for semester exam preparation.', 'Positive', 0.92, 'Analyzed', DATE_SUB(NOW(), INTERVAL 10 DAY)),
(6, 7, 'Campus', 3, 'Campus grounds and gardens are well maintained, but the cafeteria prices have increased and vegetarian options are quite limited during lunch.', 'Mixed', 0.05, 'Analyzed', DATE_SUB(NOW(), INTERVAL 9 DAY)),
(7, 8, 'Student Services', 2, 'The administrative office takes more than two weeks to verify scholarship forms. Staff response at the counter is slow and unhelpful.', 'Negative', -0.68, 'Analyzed', DATE_SUB(NOW(), INTERVAL 8 DAY)),
(8, 2, 'Course', 4, 'The database management curriculum is up to date with modern NoSQL and cloud trends. Pacing was a bit fast towards the end.', 'Positive', 0.65, 'Analyzed', DATE_SUB(NOW(), INTERVAL 7 DAY)),
(9, 3, 'Faculty', 2, 'Professors rarely reply to student emails regarding doubt clarification. Assignment grading is delayed by several weeks without rubric feedback.', 'Negative', -0.72, 'Analyzed', DATE_SUB(NOW(), INTERVAL 6 DAY)),
(10, 4, 'Infrastructure', 4, 'Campus high-speed Wi-Fi has improved significantly this semester, though speed drops noticeably near the mechanical workshop building.', 'Positive', 0.58, 'Analyzed', DATE_SUB(NOW(), INTERVAL 5 DAY)),
(11, 5, 'Laboratory', 1, 'Computer laboratory systems run slow mechanical hard drives. Compiling large C++ and Java projects takes forever. Needs SSD upgrades urgently.', 'Negative', -0.83, 'Analyzed', DATE_SUB(NOW(), INTERVAL 4 DAY)),
(12, 6, 'Teaching', 5, 'Outstanding lectures! The professor uses visual animations to explain structural mechanics which makes tricky mathematical derivations very intuitive.', 'Positive', 0.91, 'Analyzed', DATE_SUB(NOW(), INTERVAL 4 DAY)),
(13, 7, 'Overall Experience', 4, 'Great college atmosphere with plenty of hackathons and technical symposiums. Hostels are decent, overall an enriching college experience.', 'Positive', 0.78, 'Analyzed', DATE_SUB(NOW(), INTERVAL 3 DAY)),
(14, 8, 'Library', 2, 'Digital portal access credentials frequently stop working off-campus. Physical textbook copies for core subjects run out within first week.', 'Negative', -0.64, 'Analyzed', DATE_SUB(NOW(), INTERVAL 2 DAY)),
(15, 2, 'Student Services', 5, 'The training and placement cell organized remarkable mock interviews and resume workshops with industry mentors. Extremely helpful!', 'Positive', 0.89, 'Analyzed', DATE_SUB(NOW(), INTERVAL 2 DAY)),
(16, 3, 'Overall Experience', 3, 'Academic standards are satisfactory, but cultural club funding was cut and extra-curricular event schedules conflict with internal examinations.', 'Neutral', 0.02, 'Analyzed', DATE_SUB(NOW(), INTERVAL 1 DAY)),
(17, 4, 'Faculty', 4, 'Very supportive faculty who encouraged our team to publish our IoT research paper. Mentorship was top tier throughout the semester.', 'Positive', 0.82, 'Analyzed', DATE_SUB(NOW(), INTERVAL 1 DAY)),
(18, 5, 'Course', 2, 'The syllabus still covers legacy tools that are no longer used in industry. Needs immediate revision with current DevOps and cloud tools.', 'Negative', -0.61, 'Analyzed', NOW());

-- -------------------------------------------------------
-- Seed Feedback Analysis Entries
-- -------------------------------------------------------
INSERT INTO feedback_analysis (feedback_id, keywords, topics, strengths, problems, recommendations, analyzed_at) VALUES
(1, '["algorithms", "clarity", "code examples", "office hours"]', '["Faculty", "Teaching", "Mentorship"]', '["Clear concept explanations", "Helpful office hours", "Practical code examples"]', '[]', '["Continue encouraging faculty office hours and code-driven pedagogy across departments."]', DATE_SUB(NOW(), INTERVAL 14 DAY)),
(2, '["concepts", "laboratory equipment", "outdated", "oscilloscope", "lab 3"]', '["Laboratory", "Faculty", "Facilities"]', '["Clear theoretical concept explanations by faculty"]', '["Outdated laboratory equipment", "Defective oscilloscope units in lab 3"]', '["Audit and calibrate Lab 3 oscilloscopes; plan phased procurement of modern measurement instruments."]', DATE_SUB(NOW(), INTERVAL 13 DAY)),
(3, '["interactive style", "case studies", "Operating Systems", "quizzes"]', '["Teaching", "Course", "Exams"]', '["Interactive teaching style", "Real-world case studies for complex topics"]', '["Limited hands-on quiz sessions"]', '["Incorporate regular formative digital quizzes into lecture modules."]', DATE_SUB(NOW(), INTERVAL 12 DAY)),
(4, '["air conditioning", "hall 204", "broken", "blinking projector", "seminars"]', '["Infrastructure", "Facilities"]', '[]', '["Broken air conditioning in lecture hall 204", "Flickering projector during seminars"]', '["Dispatch campus maintenance team to repair AC in room 204; replace damaged projector lamp or cable."]', DATE_SUB(NOW(), INTERVAL 11 DAY)),
(5, '["research journals", "IEEE papers", "silent room", "exam preparation"]', '["Library", "Campus"]', '["Vast collection of IEEE journals", "Comfortable and quiet reading environment"]', '[]', '["Maintain journal subscriptions and expand silent reading seating capacity during peak exam weeks."]', DATE_SUB(NOW(), INTERVAL 10 DAY)),
(6, '["gardens", "well maintained", "cafeteria prices", "vegetarian options"]', '["Campus", "Student Services"]', '["Well-maintained gardens and green campus landscaping"]', '["Cafeteria price inflation", "Insufficient vegetarian meal choices"]', '["Review campus canteen pricing policy and mandate diversified healthy vegetarian meal menus."]', DATE_SUB(NOW(), INTERVAL 9 DAY)),
(7, '["administrative office", "scholarship forms", "slow staff", "unhelpful"]', '["Student Services"]', '[]', '["Slow scholarship verification workflow (> 2 weeks)", "Unresponsive help desk staff"]', '["Digitize scholarship document approvals and establish a 48-hour service level agreement (SLA) for student counters."]', DATE_SUB(NOW(), INTERVAL 8 DAY)),
(8, '["database curriculum", "NoSQL", "cloud trends", "fast pacing"]', '["Course", "Teaching"]', '["Modern curriculum featuring cloud databases and NoSQL technologies"]', '["Rushed pace towards end of semester"]', '["Rebalance course syllabus timeline to give ample practice for concluding advanced topics."]', DATE_SUB(NOW(), INTERVAL 7 DAY)),
(9, '["emails ignored", "doubt clarification", "delayed grading", "rubric"]', '["Faculty", "Assignments"]', '[]', '["Faculty unresponsiveness to student inquiry emails", "Delayed assignment return without scoring rubrics"]', '["Institute standardized communication policies and mandate transparent LMS grading rubrics within 7 days."]', DATE_SUB(NOW(), INTERVAL 6 DAY)),
(10, '["high-speed wifi", "mechanical building", "drop in speed"]', '["Infrastructure", "Campus"]', '["Significant campus Wi-Fi speed and coverage upgrade"]', '["Wi-Fi signal degradation around mechanical workshop wing"]', '["Install additional outdoor dual-band access points near mechanical engineering block."]', DATE_SUB(NOW(), INTERVAL 5 DAY)),
(11, '["hard drives", "slow systems", "compilation delay", "SSD upgrade"]', '["Laboratory", "Infrastructure"]', '[]', '["Slow mechanical hard drives causing severe compilation bottlenecks in programming labs"]', '["Execute prioritized SSD retrofitting on computer lab workstations to accelerate development environments."]', DATE_SUB(NOW(), INTERVAL 4 DAY)),
(12, '["visual animations", "structural mechanics", "mathematical derivations"]', '["Teaching", "Faculty"]', '["Dynamic visual animation pedagogy", "Intuitive explanation of complex formulas"]', '[]', '["Showcase this visual teaching methodology in departmental faculty development workshops."]', DATE_SUB(NOW(), INTERVAL 4 DAY)),
(13, '["hackathons", "technical symposiums", "hostels", "enriching"]', '["Overall Experience", "Campus"]', '["Vibrant extracurricular culture with hackathons and symposiums", "Good hostel accommodation"]', '[]', '["Sustain budget allocations for student hackathons and continue inter-collegiate technical fests."]', DATE_SUB(NOW(), INTERVAL 3 DAY)),
(14, '["digital portal", "off-campus access", "textbook shortage", "library"]', '["Library", "Infrastructure"]', '[]', '["Off-campus digital library authentication failures", "Shortage of physical core reference books"]', '["Resolve library proxy server authentication timeouts; procure additional print copies for high-demand course texts."]', DATE_SUB(NOW(), INTERVAL 2 DAY)),
(15, '["placement cell", "mock interviews", "resume workshops", "mentors"]', '["Student Services", "Overall Experience"]', '["Proactive placement training", "High quality industry mentor mock interviews"]', '[]', '["Partner with more tier-1 companies for early internship bootcamps."]', DATE_SUB(NOW(), INTERVAL 2 DAY)),
(16, '["academic standards", "cultural club", "funding cuts", "exam conflict"]', '["Overall Experience", "Campus", "Exams"]', '["Solid academic foundation"]', '["Cultural club budget cuts", "Examination schedules colliding with campus events"]', '["Coordinate academic exam calendars with student council event timetables to eliminate scheduling conflicts."]', DATE_SUB(NOW(), INTERVAL 1 DAY)),
(17, '["supportive faculty", "IoT paper", "research mentorship"]', '["Faculty", "Mentorship"]', '["Faculty encouragement for student research publications", "High-caliber semester mentorship"]', '[]', '["Provide student conference travel grants to reward faculty-mentored research publications."]', DATE_SUB(NOW(), INTERVAL 1 DAY)),
(18, '["legacy tools", "industry mismatch", "DevOps", "cloud tools"]', '["Course", "Teaching"]', '[]', '["Outdated software syllabus covering obsolete tools", "Lack of industry-standard DevOps practices"]', '["Convene academic board of studies to update curriculum with Docker, CI/CD, and modern cloud deployment modules."]', NOW());
