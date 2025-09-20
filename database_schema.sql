

-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    subscription_tier VARCHAR(20) DEFAULT 'free',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Problem Statements  
CREATE TABLE problem_statements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    problem_type VARCHAR(50) NOT NULL,
    constraints JSONB DEFAULT '{}',
    objectives JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Notebooks
CREATE TABLE notebooks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    problem_id UUID REFERENCES problem_statements(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    deap_toolbox_config JSONB DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'draft',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Notebook Cells
CREATE TABLE notebook_cells (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    notebook_id UUID REFERENCES notebooks(id) ON DELETE CASCADE,
    cell_type VARCHAR(20) NOT NULL,
    code TEXT DEFAULT '',
    agent_id VARCHAR(50),
    version INTEGER DEFAULT 1,
    position INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Evolution Sessions
CREATE TABLE evolution_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    notebook_id UUID REFERENCES notebooks(id) ON DELETE CASCADE,
    current_iteration INTEGER DEFAULT 0,
    max_iterations INTEGER DEFAULT 5,
    best_fitness FLOAT,
    status VARCHAR(20) DEFAULT 'pending',
    session_config JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Evolution Steps
CREATE TABLE evolution_steps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES evolution_sessions(id) ON DELETE CASCADE,
    iteration INTEGER NOT NULL,
    agent_id VARCHAR(50) NOT NULL,
    generated_code TEXT,
    fitness_improvement FLOAT,
    token_usage INTEGER DEFAULT 0,
    reasoning TEXT,
    execution_time FLOAT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Chat Threads for organizing conversations
CREATE TABLE chat_threads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    notebook_id UUID REFERENCES notebooks(id) ON DELETE CASCADE,
    title VARCHAR(200),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    message_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true
);

-- Chat Messages (extends LangChain message_store)
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    notebook_id UUID REFERENCES notebooks(id) ON DELETE CASCADE,
    thread_id UUID REFERENCES chat_threads(id) ON DELETE SET NULL,
    parent_message_id UUID REFERENCES chat_messages(id) ON DELETE SET NULL,
    message TEXT NOT NULL,
    sender VARCHAR(50) NOT NULL,
    message_type VARCHAR(30) DEFAULT 'user_input',
    iteration_context INTEGER,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Chat Context Summaries
CREATE TABLE chat_context_summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    notebook_id UUID REFERENCES notebooks(id) ON DELETE CASCADE,
    context_summary TEXT,
    message_range_start TIMESTAMP WITH TIME ZONE,
    message_range_end TIMESTAMP WITH TIME ZONE,
    token_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_current BOOLEAN DEFAULT true
);

-- Program Database (OpenEvolve inspired)
CREATE TABLE program_database (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    notebook_id UUID REFERENCES notebooks(id) ON DELETE CASCADE,
    program_code TEXT NOT NULL,
    program_type VARCHAR(50) NOT NULL,
    deap_operators JSONB DEFAULT '{}',
    performance_metrics JSONB DEFAULT '{}',
    problem_characteristics JSONB DEFAULT '{}',
    test_results JSONB DEFAULT '{}',
    generation INTEGER DEFAULT 1,
    parent_program_id UUID REFERENCES program_database(id) ON DELETE SET NULL,
    is_best_performer BOOLEAN DEFAULT false,
    tags VARCHAR(255)[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Evaluator Results
CREATE TABLE evaluator_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    program_id UUID REFERENCES program_database(id) ON DELETE CASCADE,
    evaluator_type VARCHAR(50) NOT NULL,
    test_input JSONB,
    expected_output JSONB,
    actual_output JSONB,
    score FLOAT,
    execution_time FLOAT,
    memory_usage FLOAT,
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    evaluated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Persistent Sessions
CREATE TABLE persistent_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    notebook_id UUID REFERENCES notebooks(id) ON DELETE CASCADE,
    session_data JSONB DEFAULT '{}',
    agent_states JSONB DEFAULT '{}',
    variables JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true
);

-- LangChain message store table (for PostgresChatMessageHistory)
CREATE TABLE message_store (
    session_id VARCHAR NOT NULL,
    message_id VARCHAR NOT NULL,
    message JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (session_id, message_id)
);

-- Indexes for Performance
CREATE INDEX idx_notebooks_problem_id ON notebooks(problem_id);
CREATE INDEX idx_notebook_cells_notebook_id ON notebook_cells(notebook_id);
CREATE INDEX idx_chat_messages_notebook_id ON chat_messages(notebook_id);
CREATE INDEX idx_chat_messages_thread_id ON chat_messages(thread_id);
CREATE INDEX idx_evolution_sessions_notebook_id ON evolution_sessions(notebook_id);
CREATE INDEX idx_evolution_steps_session_id ON evolution_steps(session_id);
CREATE INDEX idx_program_database_notebook_id ON program_database(notebook_id);
CREATE INDEX idx_program_database_best ON program_database(notebook_id, is_best_performer) WHERE is_best_performer = true;
CREATE INDEX idx_message_store_session_id ON message_store(session_id);

-- Full-text search indexes
CREATE INDEX idx_chat_messages_fts ON chat_messages USING gin(to_tsvector('english', message));
CREATE INDEX idx_program_database_code_fts ON program_database USING gin(to_tsvector('english', program_code));