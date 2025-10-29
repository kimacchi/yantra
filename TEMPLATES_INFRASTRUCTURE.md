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

## Template Auto-Loading System

Templates are now automatically loaded into the database when the API starts!

### Implementation

**Location**: `api/templates/`

**Files**:
- `definitions.py` - 22 pre-defined language templates
- `seed.py` - Seeding logic (idempotent)
- `__init__.py` - Package initialization
- `README.md` - Detailed documentation

**Languages Included**:
- Python 3.12, Python 3.11 Data Science
- Node.js 20 LTS, Node.js 18 LTS, TypeScript 5
- Go 1.22, Rust Stable
- Java 21 LTS, Java 17 LTS
- .NET 8 (C#)
- PHP 8.3, PHP 8.2
- GCC (C/C++)
- Ruby 3.3, Perl 5, R 4, Lua 5.4
- Swift 5, Kotlin JVM, Scala 3
- Elixir 1.16, Haskell 9

### How It Works

1. API startup triggers `@app.on_event("startup")` in `main.py`
2. `seed_templates(db)` is called from `templates/seed.py`
3. Templates from `definitions.py` are checked against the database
4. New templates are inserted; existing ones are skipped (idempotent)
5. Results are logged to console

### Adding New Templates

Simply edit `api/templates/definitions.py` and restart the API:

```python
LANGUAGE_TEMPLATES.append({
    "id": "mylang-1.0",
    "name": "MyLang 1.0",
    "description": "Your language description",
    "category": "language",
    "dockerfile_template": "FROM ...",
    "default_run_command": ["mylang"],
    "tags": ["mylang", "tag2"],
    "icon": "🔥",
    "author": "yantra",
    "is_official": True,
})
```

See `api/templates/README.md` for full documentation.

## API Documentation

Once the server is running, full API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
