-- Migration: Memory Maintenance Infrastructure
-- Date: 2025-08-11
-- Purpose: Add soft-delete support and indexes for memory maintenance operations

-- Add deleted_at columns for soft-delete functionality
ALTER TABLE user_sessions 
ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP NULL;

ALTER TABLE user_preferences 
ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP NULL;

ALTER TABLE user_activity_logs 
ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP NULL;

ALTER TABLE user_conversations 
ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP NULL;

ALTER TABLE user_memory 
ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP NULL;

ALTER TABLE user_embeddings 
ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP NULL;

-- Add created_at columns if they don't exist (for TTL cleanup)
ALTER TABLE user_sessions 
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE user_preferences 
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE user_activity_logs 
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE user_conversations 
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE user_memory 
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE user_embeddings 
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Create indexes for efficient cleanup operations
-- These indexes support both TTL cleanup and user forget operations

-- Indexes for TTL cleanup (created_at + deleted_at)
CREATE INDEX IF NOT EXISTS idx_user_sessions_cleanup 
ON user_sessions(created_at, deleted_at) 
WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_user_preferences_cleanup 
ON user_preferences(created_at, deleted_at) 
WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_user_activity_logs_cleanup 
ON user_activity_logs(created_at, deleted_at) 
WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_user_conversations_cleanup 
ON user_conversations(created_at, deleted_at) 
WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_user_memory_cleanup 
ON user_memory(created_at, deleted_at) 
WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_user_embeddings_cleanup 
ON user_embeddings(created_at, deleted_at) 
WHERE deleted_at IS NULL;

-- Indexes for user forget operations (user_id + deleted_at)
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_forget 
ON user_sessions(user_id, deleted_at) 
WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_user_preferences_user_forget 
ON user_preferences(user_id, deleted_at) 
WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_user_activity_logs_user_forget 
ON user_activity_logs(user_id, deleted_at) 
WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_user_conversations_user_forget 
ON user_conversations(user_id, deleted_at) 
WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_user_memory_user_forget 
ON user_memory(user_id, deleted_at) 
WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_user_embeddings_user_forget 
ON user_embeddings(user_id, deleted_at) 
WHERE deleted_at IS NULL;

-- Create a maintenance log table for tracking cleanup operations
CREATE TABLE IF NOT EXISTS maintenance_log (
    id SERIAL PRIMARY KEY,
    operation_type VARCHAR(50) NOT NULL, -- 'ttl_cleanup', 'forget_user', etc.
    table_name VARCHAR(100),
    user_id VARCHAR(255),
    records_affected INTEGER DEFAULT 0,
    parameters JSONB,
    status VARCHAR(20) DEFAULT 'running', -- 'running', 'completed', 'failed'
    error_message TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    duration_ms INTEGER,
    pipeline_id VARCHAR(100),
    pipeline_version VARCHAR(100)
);

-- Index for maintenance log queries
CREATE INDEX IF NOT EXISTS idx_maintenance_log_operation 
ON maintenance_log(operation_type, started_at);

CREATE INDEX IF NOT EXISTS idx_maintenance_log_status 
ON maintenance_log(status, started_at);

-- Create a function for automatic maintenance logging
CREATE OR REPLACE FUNCTION log_maintenance_operation(
    p_operation_type VARCHAR,
    p_table_name VARCHAR DEFAULT NULL,
    p_user_id VARCHAR DEFAULT NULL,
    p_records_affected INTEGER DEFAULT 0,
    p_parameters JSONB DEFAULT NULL,
    p_status VARCHAR DEFAULT 'completed',
    p_error_message TEXT DEFAULT NULL,
    p_pipeline_id VARCHAR DEFAULT NULL,
    p_pipeline_version VARCHAR DEFAULT NULL
) RETURNS INTEGER AS $$
DECLARE
    log_id INTEGER;
BEGIN
    INSERT INTO maintenance_log (
        operation_type,
        table_name,
        user_id,
        records_affected,
        parameters,
        status,
        error_message,
        completed_at,
        pipeline_id,
        pipeline_version
    ) VALUES (
        p_operation_type,
        p_table_name,
        p_user_id,
        p_records_affected,
        p_parameters,
        p_status,
        p_error_message,
        CURRENT_TIMESTAMP,
        p_pipeline_id,
        p_pipeline_version
    ) RETURNING id INTO log_id;
    
    RETURN log_id;
END;
$$ LANGUAGE plpgsql;

-- Create maintenance configuration table
CREATE TABLE IF NOT EXISTS maintenance_config (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(100)
);

-- Insert default maintenance configurations
INSERT INTO maintenance_config (config_key, config_value, description, updated_by) 
VALUES 
    ('ttl_cleanup_days', '30', 'Default number of days for TTL cleanup', 'migration'),
    ('ttl_cleanup_batch_size', '1000', 'Default batch size for TTL cleanup operations', 'migration'),
    ('forget_user_batch_size', '1000', 'Default batch size for user forget operations', 'migration'),
    ('maintenance_enabled', 'true', 'Global maintenance operations enabled flag', 'migration')
ON CONFLICT (config_key) DO NOTHING;

-- Create view for active (non-deleted) records
CREATE OR REPLACE VIEW v_active_user_sessions AS
SELECT * FROM user_sessions WHERE deleted_at IS NULL;

CREATE OR REPLACE VIEW v_active_user_preferences AS
SELECT * FROM user_preferences WHERE deleted_at IS NULL;

CREATE OR REPLACE VIEW v_active_user_activity_logs AS
SELECT * FROM user_activity_logs WHERE deleted_at IS NULL;

CREATE OR REPLACE VIEW v_active_user_conversations AS
SELECT * FROM user_conversations WHERE deleted_at IS NULL;

CREATE OR REPLACE VIEW v_active_user_memory AS
SELECT * FROM user_memory WHERE deleted_at IS NULL;

CREATE OR REPLACE VIEW v_active_user_embeddings AS
SELECT * FROM user_embeddings WHERE deleted_at IS NULL;

-- Grant permissions for the maintenance operations
GRANT SELECT, UPDATE ON ALL TABLES IN SCHEMA public TO maintenance_user;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO maintenance_user;
GRANT EXECUTE ON FUNCTION log_maintenance_operation TO maintenance_user;

-- Migration completion log
INSERT INTO maintenance_log (
    operation_type,
    records_affected,
    status,
    parameters,
    pipeline_id,
    pipeline_version
) VALUES (
    'migration_2025_08_11',
    0,
    'completed',
    '{"migration_file": "2025_08_11_memory_maintenance.sql", "description": "Added soft-delete support and indexes for memory maintenance"}',
    '22d71a78a',
    '10aba09e5a'
);

COMMIT;
