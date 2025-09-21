# EA Code Evolution Platform

A microservice that evolves DEAP-based evolutionary algorithm code using ChatGroq LLM and multi-agent coordination. The platform automatically generates, optimizes, and evolves evolutionary algorithms for real-world optimization problems.

## Current Status: Multi-Agent Code Generation System (Modules 1-4 Complete)

**What Works:** Multi-agent system that generates complete, working DEAP evolutionary algorithms
**What's Missing:** Actual code evolution, execution, and iterative improvement loops

---

## Table of Contents

- [Project Overview](#project-overview)
- [Current Implementation Status](#current-implementation-status)
- [Architecture](#architecture)
- [Features Implemented](#features-implemented)
- [Installation & Setup](#installation--setup)
- [API Documentation](#api-documentation)
- [Testing](#testing)
---

## Project Overview

EVoC v2 - EA Code Evolution Platform aims to automatically generate and evolve evolutionary algorithms using a multi-agent system powered by LLMs. Users describe optimization problems, and the system generates complete DEAP-compatible solutions through coordinated AI agents.
### Key Innovation
Instead of manually coding evolutionary algorithms, users describe their problem and specialized AI agents collaborate to generate, test, and iteratively improve complete EA solutions.

---

## Current Implementation Status

### COMPLETED (Modules 1-4)

#### Module 1: Foundation & Database
- **PostgreSQL Database** - Complete schema with foreign key constraints
- **Pydantic Models** - Type-safe data models for all entities
- **Configuration Management** - Environment-based settings
- **Authentication System** - JWT-based user management

#### Module 2: FastAPI Application & CRUD
- **RESTful API** - Complete CRUD operations for users, problems, notebooks
- **Authentication Endpoints** - Registration, login, user management
- **Problem Management** - Create and manage optimization problems
- **Notebook System** - Workspace for EA solution development
- **Error Handling** - Comprehensive error responses and logging

#### Module 3: ChatGroq Integration
- **ChatGroq Service** - Async LLM client with retry logic
- **Chat History** - Persistent conversation management
- **Context Management** - Token optimization and compression
- **Basic Code Generation** - Single-shot code generation endpoints

#### Module 4: Multi-Agent System 
- **7 Specialized Agents** - Problem analysis, individuals modeling, fitness, crossover, mutation, selection, integration
- **Agent Coordination** - Sequential execution with context sharing
- **Cell-Based Storage** - Generated code stored in versioned notebook cells
- **Complete DEAP Integration** - Generates working evolutionary algorithms
- **Individual Cell Regeneration** - Iterative improvement of specific components

### NOT YET IMPLEMENTED

#### Module 5: Evolution Engine (Critical Missing Piece)
- **Code Execution** - Running generated algorithms in sandbox
- **Performance Evaluation** - Measuring algorithm effectiveness
- **Evolution Loop** - Iterative improvement based on results
- **Fitness Tracking** - Monitoring algorithm performance over generations

#### Module 6: Code Execution Environment
- **Docker Sandboxing** - Safe code execution environment
- **Resource Management** - CPU/memory limits and timeouts
- **Error Handling** - Execution error capture and reporting
- **Results Analysis** - Performance metrics and visualization

#### Module 7: Program Database (OpenEvolve-Inspired)
- **Algorithm Storage** - Evolved code variants with lineage tracking
- **Performance History** - Historical performance metrics
- **Algorithm Reuse** - Similarity search and recommendation
- **Knowledge Base** - Patterns and best practices

#### Module 8: Advanced Evolution Features
- **Multi-Population Evolution** - Parallel algorithm evolution
- **Hyperparameter Optimization** - EA parameter tuning
- **Algorithm Hybridization** - Combining successful patterns
- **Real-time Monitoring** - Evolution progress visualization

---

## Architecture

![Architecture Diagram](asset\images\arch.png)



---

## Features Implemented

### 🔐 Authentication & User Management
- JWT-based authentication
- User registration and login
- Secure password hashing
- Session management

### 📋 Problem Management
- Create optimization problems with constraints and objectives
- Support for multiple problem types (optimization, scheduling, routing)
- Rich problem descriptions with metadata
- Problem search and filtering

### 📓 Notebook System
- Jupyter-like workspace for EA development
- Cell-based code organization
- Version control for generated code
- DEAP configuration management

### 🤖 Multi-Agent Code Generation
- **Problem Analyser Agent** - Analyzes requirements and sets up DEAP structure
- **Individuals Modelling Agent** - Designs solution representation
- **Fitness Function Agent** - Creates multi-objective evaluation functions
- **Crossover Function Agent** - Generates recombination operators
- **Mutation Function Agent** - Creates variation operators
- **Selection Strategy Agent** - Implements parent selection methods
- **Code Integration Agent** - Assembles complete DEAP algorithm

### 💬 Chat System
- Conversational AI assistance
- Chat history persistence
- Context-aware responses
- Integration with agent-generated code

### 🔄 Cell Management
- Automatic code storage in notebook cells
- Version tracking for iterative improvements
- Individual cell regeneration
- Agent attribution and metadata

---

## Installation & Setup

### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- Redis (optional, for caching)
- ChatGroq API key (free tier available for now)

### 1. Clone Repository
```bash
git clone https://github.com/Astrasv/EVoCv2_LLM_Pipeline
cd EVoCv2_LLM_Pipeline

```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
```bash
# Create PostgreSQL database
createdb evoc_db

# Run schema (use the updated schema with foreign key constraints)
psql -d evoc_db -f database_schema.sql
```

### 5. Environment Configuration
Create `.env` file:
```bash
# Database
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/evoc_db

# ChatGroq API
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# Security
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256

# Application
DEBUG=true
HOST=0.0.0.0
PORT=8000
```

### 6. Run Application
```bash
python -m src.main
```

Access the application:
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/v1/health

---

## API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Authentication
All endpoints except health checks require JWT authentication:
```
Authorization: Bearer <your_jwt_token>
```


## Testing

### Comprehensive Test Suite
```bash
# Run complete API test (Modules 1-4)
python test_api_full.py
# Test database setup
python test_setup.py

```


### What's Missing
- **No actual evolution** - algorithms are generated once, not improved iteratively
- **No execution** - generated code isn't run or tested
- **No performance feedback** - can't tell if generated algorithms are effective
- **No learning** - agents don't improve based on past successes/failures






**Current Status:** Working multi-agent DEAP code generator
**Next Milestone:** Evolution engine with code execution and iterative improvement
**Vision:** Complete evolutionary algorithm evolution platform with learning and optimization