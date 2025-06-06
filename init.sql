-- Initialize the database with some sample data
-- This script runs automatically when PostgreSQL container starts

-- Create database (if not exists)
\c minilab2;

-- Insert sample users
INSERT INTO users (username, email, created_at, is_active) VALUES
    ('john_doe', 'john@example.com', NOW(), true),
    ('jane_smith', 'jane@example.com', NOW(), true),
    ('bob_wilson', 'bob@example.com', NOW(), true)
ON CONFLICT (username) DO NOTHING;

-- Insert sample tasks
INSERT INTO tasks (title, description, user_id, completed, created_at, updated_at) VALUES
    ('Setup Development Environment', 'Configure Docker, PostgreSQL, and FastAPI', 1, true, NOW(), NOW()),
    ('Create API Documentation', 'Document all API endpoints using OpenAPI/Swagger', 1, false, NOW(), NOW()),
    ('Design Database Schema', 'Create ERD and implement database tables', 2, false, NOW(), NOW()),
    ('Implement User Authentication', 'Add JWT-based authentication system', 2, false, NOW(), NOW()),
    ('Build Streamlit Dashboard', 'Create interactive dashboard for data visualization', 3, true, NOW(), NOW()),
    ('Write Unit Tests', 'Add comprehensive test coverage for backend API', 3, false, NOW(), NOW()),
    ('Deploy to Production', 'Set up CI/CD pipeline and deploy to cloud', 1, false, NOW(), NOW())
ON CONFLICT DO NOTHING;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_completed ON tasks(completed);
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at);

-- Create a view for task statistics
CREATE OR REPLACE VIEW task_stats AS
SELECT 
    u.id as user_id,
    u.username,
    u.email,
    COUNT(t.id) as total_tasks,
    COUNT(CASE WHEN t.completed = true THEN 1 END) as completed_tasks,
    COUNT(CASE WHEN t.completed = false THEN 1 END) as pending_tasks,
    ROUND(
        (COUNT(CASE WHEN t.completed = true THEN 1 END)::float / 
         NULLIF(COUNT(t.id), 0) * 100), 2
    ) as completion_percentage
FROM users u
LEFT JOIN tasks t ON u.id = t.user_id
GROUP BY u.id, u.username, u.email;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;