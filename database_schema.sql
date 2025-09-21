-- Users (no foreign keys)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    subscription_tier VARCHAR(20) DEFAULT 'free',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Problem Statements with proper FK to users
CREATE TABLE problem_statements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    problem_type VARCHAR(50) NOT NULL,
    constraints JSONB DEFAULT '{}',
    objectives JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT fk_problem_user 
        FOREIGN KEY (user_id) 
        REFERENCES users(id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
);

-- Notebooks with proper FK to problem_statements
CREATE TABLE notebooks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    problem_id UUID NOT NULL,
    name VARCHAR(100) NOT NULL,
    deap_toolbox_config JSONB DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'draft',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT fk_notebook_problem 
        FOREIGN KEY (problem_id) 
        REFERENCES problem_statements(id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
);

-- Notebook Cells with proper FK to notebooks
CREATE TABLE notebook_cells (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    notebook_id UUID NOT NULL,
    cell_type VARCHAR(20) NOT NULL,
    code TEXT DEFAULT '',
    agent_id VARCHAR(50),
    version INTEGER DEFAULT 1,
    position INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT fk_cell_notebook 
        FOREIGN KEY (notebook_id) 
        REFERENCES notebooks(id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
);

-- Evolution Sessions with proper FK to notebooks
CREATE TABLE evolution_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    notebook_id UUID NOT NULL,
    current_iteration INTEGER DEFAULT 0,
    max_iterations INTEGER DEFAULT 5,
    best_fitness FLOAT,
    status VARCHAR(20) DEFAULT 'pending',
    session_config JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT fk_session_notebook 
        FOREIGN KEY (notebook_id) 
        REFERENCES notebooks(id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
);

-- Evolution Steps with proper FK to evolution_sessions
CREATE TABLE evolution_steps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL,
    iteration INTEGER NOT NULL,
    agent_id VARCHAR(50) NOT NULL,
    generated_code TEXT,
    fitness_improvement FLOAT,
    token_usage INTEGER DEFAULT 0,
    reasoning TEXT,
    execution_time FLOAT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT fk_step_session 
        FOREIGN KEY (session_id) 
        REFERENCES evolution_sessions(id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
);

-- Chat Threads with proper FK to notebooks
CREATE TABLE chat_threads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    notebook_id UUID NOT NULL,
    title VARCHAR(200),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    message_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    
    CONSTRAINT fk_thread_notebook 
        FOREIGN KEY (notebook_id) 
        REFERENCES notebooks(id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
);

-- Chat Messages with proper FKs
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    notebook_id UUID NOT NULL,
    thread_id UUID,
    parent_message_id UUID,
    message TEXT NOT NULL,
    sender VARCHAR(50) NOT NULL,
    message_type VARCHAR(30) DEFAULT 'user_input',
    iteration_context INTEGER,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT fk_message_notebook 
        FOREIGN KEY (notebook_id) 
        REFERENCES notebooks(id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
        
    CONSTRAINT fk_message_thread 
        FOREIGN KEY (thread_id) 
        REFERENCES chat_threads(id) 
        ON DELETE SET NULL 
        ON UPDATE CASCADE,
        
    CONSTRAINT fk_message_parent 
        FOREIGN KEY (parent_message_id) 
        REFERENCES chat_messages(id) 
        ON DELETE SET NULL 
        ON UPDATE CASCADE
);

-- Chat Context Summaries with proper FK to notebooks
CREATE TABLE chat_context_summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    notebook_id UUID NOT NULL,
    context_summary TEXT,
    message_range_start TIMESTAMP WITH TIME ZONE,
    message_range_end TIMESTAMP WITH TIME ZONE,
    token_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_current BOOLEAN DEFAULT true,
    
    CONSTRAINT fk_context_notebook 
        FOREIGN KEY (notebook_id) 
        REFERENCES notebooks(id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
);

-- Program Database with proper FKs
CREATE TABLE program_database (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    notebook_id UUID NOT NULL,
    program_code TEXT NOT NULL,
    program_type VARCHAR(50) NOT NULL,
    deap_operators JSONB DEFAULT '{}',
    performance_metrics JSONB DEFAULT '{}',
    problem_characteristics JSONB DEFAULT '{}',
    test_results JSONB DEFAULT '{}',
    generation INTEGER DEFAULT 1,
    parent_program_id UUID,
    is_best_performer BOOLEAN DEFAULT false,
    tags VARCHAR(255)[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT fk_program_notebook 
        FOREIGN KEY (notebook_id) 
        REFERENCES notebooks(id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
        
    CONSTRAINT fk_program_parent 
        FOREIGN KEY (parent_program_id) 
        REFERENCES program_database(id) 
        ON DELETE SET NULL 
        ON UPDATE CASCADE
);

-- Evaluator Results with proper FK to program_database
CREATE TABLE evaluator_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    program_id UUID NOT NULL,
    evaluator_type VARCHAR(50) NOT NULL,
    test_input JSONB,
    expected_output JSONB,
    actual_output JSONB,
    score FLOAT,
    execution_time FLOAT,
    memory_usage FLOAT,
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    evaluated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT fk_result_program 
        FOREIGN KEY (program_id) 
        REFERENCES program_database(id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
);

-- Persistent Sessions with proper FK to notebooks
CREATE TABLE persistent_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    notebook_id UUID NOT NULL,
    session_data JSONB DEFAULT '{}',
    agent_states JSONB DEFAULT '{}',
    variables JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true,
    
    CONSTRAINT fk_persistent_notebook 
        FOREIGN KEY (notebook_id) 
        REFERENCES notebooks(id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
);

-- LangChain message store table (no foreign keys needed)
CREATE TABLE message_store (
    session_id VARCHAR NOT NULL,
    message_id VARCHAR NOT NULL,
    message JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (session_id, message_id)
);

-- Indexes for Performance (same as before)
CREATE INDEX idx_notebooks_problem_id ON notebooks(problem_id);
CREATE INDEX idx_notebook_cells_notebook_id ON notebook_cells(notebook_id);
CREATE INDEX idx_chat_messages_notebook_id ON chat_messages(notebook_id);
CREATE INDEX idx_chat_messages_thread_id ON chat_messages(thread_id);
CREATE INDEX idx_evolution_sessions_notebook_id ON evolution_sessions(notebook_id);
CREATE INDEX idx_evolution_steps_session_id ON evolution_steps(session_id);
CREATE INDEX idx_program_database_notebook_id ON program_database(notebook_id);
CREATE INDEX idx_program_database_best ON program_database(notebook_id, is_best_performer) WHERE is_best_performer = true;
CREATE INDEX idx_message_store_session_id ON message_store(session_id);

-- Full-text search indexes (same as before)
CREATE INDEX idx_chat_messages_fts ON chat_messages USING gin(to_tsvector('english', message));
CREATE INDEX idx_program_database_code_fts ON program_database USING gin(to_tsvector('english', program_code));

-- Additional constraints for data integrity
ALTER TABLE users ADD CONSTRAINT check_email_format 
    CHECK (email ~* '^[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

ALTER TABLE problem_statements ADD CONSTRAINT check_problem_type 
    CHECK (problem_type IN ('optimization', 'scheduling', 'routing', 'classification', 'regression', 'other'));

ALTER TABLE notebooks ADD CONSTRAINT check_notebook_status 
    CHECK (status IN ('draft', 'evolving', 'completed', 'archived'));

ALTER TABLE notebook_cells ADD CONSTRAINT check_cell_type 
    CHECK (cell_type IN (
        'fitness', 'selection', 'crossover', 'mutation', 
        'initialization', 'evaluation', 'custom',
        'problem_analysis', 'individual_representation', 'toolbox_registration'
    ));

ALTER TABLE evolution_sessions ADD CONSTRAINT check_iterations 
    CHECK (current_iteration >= 0 AND max_iterations > 0 AND current_iteration <= max_iterations);

ALTER TABLE evolution_sessions ADD CONSTRAINT check_session_status 
    CHECK (status IN ('pending', 'running', 'paused', 'completed', 'failed', 'cancelled'));

ALTER TABLE chat_messages ADD CONSTRAINT check_message_type 
    CHECK (message_type IN ('user_input', 'ai_response', 'agent_response', 'system_notification', 'code_generation'));

ALTER TABLE program_database ADD CONSTRAINT check_program_type 
    CHECK (program_type IN ('complete_algorithm', 'fitness_function', 'selection_operator', 'crossover_operator', 'mutation_operator', 'custom'));

ALTER TABLE evaluator_results ADD CONSTRAINT check_evaluator_type 
    CHECK (evaluator_type IN ('fitness', 'performance', 'correctness', 'efficiency', 'custom'));