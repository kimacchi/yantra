# Dockerfile Templates Infrastructure

## Overview
Added infrastructure to support Dockerfile templates that users can browse and use as starting points for creating custom compiler images.

## Backend Changes

### 1. Database Schema (`migrations/002_add_templates.sql`)
Created `dockerfile_templates` table with:
- `id` - Unique identifier
- `name` - Display name
- `description` - Template description
- `category` - Template category (language, framework, tool, os)
- `dockerfile_template` - The Dockerfile content
- `default_run_command` - Suggested run command (JSON array)
- `tags` - Tags for search/filtering (JSON array)
- `icon` - Icon or emoji identifier
- `author` - Template author
- `is_official` - Official template flag
- Timestamps (created_at, updated_at)

### 2. SQLAlchemy Model (`api/models/database.py`)
Added `DockerfileTemplate` model mapping to the database table.

### 3. API Schemas (`api/models/schemas.py`)
Added:
- `TemplateResponse` - Response schema for template data
- `CreateTemplateRequest` - Request schema for creating templates

### 4. Controller (`api/controllers/template_controller.py`)
Created `TemplateController` with methods:
- `create_template()` - Create a new template
- `list_templates()` - List templates with optional filtering by category and official status
- `get_template()` - Get a specific template by ID
- `delete_template()` - Delete a template

### 5. API Router (`api/routers/templates.py`)
Created REST endpoints:
- `POST /templates` - Create template
- `GET /templates` - List templates (supports `?category=` and `?official_only=` filters)
- `GET /templates/{id}` - Get specific template
- `DELETE /templates/{id}` - Delete template

### 6. Main App (`api/main.py`)
- Registered templates router
- Added Templates tag to OpenAPI documentation

## Frontend Changes

### 1. Types (`client/src/types/template.ts`)
Defined TypeScript interfaces:
- `DockerfileTemplate` - Template data structure
- `CreateTemplateRequest` - Template creation request

### 2. API Client (`client/src/api/templateApi.ts`)
Created API client functions:
- `listTemplates()` - Fetch templates with filters
- `getTemplate()` - Fetch single template
- `createTemplate()` - Create template (admin)
- `deleteTemplate()` - Delete template (admin)

### 3. Templates Page (`client/src/pages/TemplatesPage.tsx`)
Created template browsing page with:
- Grid view of all templates
- Category and official-only filters
- Template cards showing name, description, category, tags
- Click to view full template details in modal
- "Use Template" button to navigate to compiler creation with template pre-filled

### 4. Navigation
- Updated `App.tsx` to add `/templates` route
- Updated `Navbar.tsx` to add Templates link
- Updated `CreateCompilerPage.tsx` to accept template data from navigation state and show template info when pre-filled

## How It Works

1. **Browse Templates**: Users navigate to `/templates` to see all available Dockerfile templates
2. **Filter**: Users can filter by category or show only official templates
3. **View Details**: Click on a template card to see full Dockerfile content and run command
4. **Use Template**: Click "Use Template" button to navigate to compiler creation page with template data pre-filled
5. **Create Compiler**: The compiler form is automatically populated with the template's Dockerfile and run command

## Next Steps

To add actual templates to the system:

1. Run the migration: `psql -d yantra -f migrations/002_add_templates.sql`
2. Add templates via API or directly in the database
3. Example template creation:
```bash
curl -X POST http://localhost:8000/api/templates \
  -H "Content-Type: application/json" \
  -d '{
    "id": "python-base",
    "name": "Python Base",
    "description": "Base Python runtime for general-purpose scripting",
    "category": "language",
    "dockerfile_template": "FROM python:3.11-slim\nWORKDIR /sandbox\nRUN useradd -m -u 1000 sandbox && chown sandbox:sandbox /sandbox\nUSER sandbox\nCMD [\"python\", \"-\"]",
    "default_run_command": ["python", "-"],
    "tags": ["python", "general"],
    "icon": "🐍",
    "author": "yantra",
    "is_official": true
  }'
```

## API Documentation

Once the server is running, full API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
