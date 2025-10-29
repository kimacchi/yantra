# Dockerfile Templates

This directory contains Dockerfile template definitions that are automatically seeded into the database when the Yantra API starts.

## Structure

```
templates/
├── __init__.py         # Package initialization, exports seed_templates
├── definitions.py      # Language template definitions
├── seed.py            # Seeding logic and utilities
└── README.md          # This file
```

## Files

### `definitions.py`
Contains `LANGUAGE_TEMPLATES` - a list of dictionaries defining Dockerfile templates for popular programming languages.

**Current Templates (22 languages):**
- Python 3.12, Python 3.11 Data Science
- Node.js 20 LTS, Node.js 18 LTS
- TypeScript 5
- Go 1.22
- Rust Stable
- Java 21 LTS, Java 17 LTS
- .NET 8 (C#)
- PHP 8.3, PHP 8.2
- GCC (C/C++)
- Ruby 3.3
- Perl 5
- R 4
- Lua 5.4
- Swift 5
- Kotlin JVM
- Scala 3
- Elixir 1.16
- Haskell 9

**Template Structure:**
```python
{
    "id": "unique-identifier",
    "name": "Display Name",
    "description": "Template description",
    "category": "language",  # or "framework", "tool", "os"
    "dockerfile_template": "FROM ...\nWORKDIR ...\n...",
    "default_run_command": ["command", "args"],
    "tags": ["tag1", "tag2"],
    "icon": "🐍",
    "author": "yantra",
    "is_official": True
}
```

### `seed.py`
Contains seeding logic with two main functions:

#### `seed_templates(db: Session) -> Dict[str, Any]`
Default seeding function called on API startup. Idempotent - only adds new templates, skips existing ones.

**Returns:**
```python
{
    "added": ["template-id-1", "template-id-2"],
    "skipped": ["existing-template-id"],
    "updated": [],
    "errors": []
}
```

#### `update_existing_templates(db: Session) -> Dict[str, Any]`
Force updates existing templates with new definitions. Use when you want to sync template changes to the database.

## How It Works

1. **API Startup**: When the FastAPI application starts (`main.py`), the `@app.on_event("startup")` handler is triggered
2. **Database Session**: A database session is created
3. **Template Seeding**: `seed_templates(db)` is called
4. **Idempotent Check**: For each template in `LANGUAGE_TEMPLATES`:
   - Check if template ID exists in database
   - If exists: skip it
   - If not exists: insert it
5. **Commit**: All new templates are committed in a single transaction
6. **Logging**: Results are logged to console

## Adding New Templates

To add a new language template:

1. Open `definitions.py`
2. Add a new dictionary to the `LANGUAGE_TEMPLATES` list:
```python
{
    "id": "mylang-1.0",
    "name": "MyLang 1.0",
    "description": "Description of the language and use case",
    "category": "language",
    "dockerfile_template": """FROM mylang:1.0-slim
WORKDIR /sandbox
RUN useradd -m -u 1000 sandbox && chown sandbox:sandbox /sandbox
USER sandbox
CMD ["mylang"]""",
    "default_run_command": ["mylang"],
    "tags": ["mylang", "scripting"],
    "icon": "🔥",
    "author": "yantra",
    "is_official": True,
}
```
3. Restart the API - the new template will be automatically added

## Updating Existing Templates

By default, existing templates are **not updated** on startup to avoid overwriting user modifications.

To force update all templates:

1. In `main.py`, change the startup handler:
```python
from templates import update_existing_templates

@app.on_event("startup")
async def startup_event():
    # ...
    results = update_existing_templates(db)  # Instead of seed_templates(db)
    # ...
```

2. Or create a one-time migration script to update templates

## Security Best Practices

All templates follow these security guidelines:

1. **Non-root user**: Run processes as `sandbox` user (UID 1000)
2. **Minimal base images**: Use slim/alpine variants when possible
3. **Defined working directory**: Use `/sandbox` as working directory
4. **Clean up**: Remove unnecessary packages after installation
5. **No cache**: Use `--no-cache-dir` for package managers

## Testing Templates

To test a template before adding it to production:

1. Add it to `definitions.py`
2. Restart the API in development mode
3. Check the logs for seeding results
4. Test via the API:
```bash
curl http://localhost:8000/api/templates
curl http://localhost:8000/api/templates/your-template-id
```

## Logs

When the API starts, you'll see logs like:

```
INFO:     🚀 Yantra API starting up...
INFO:     📦 Seeding Dockerfile templates...
INFO:     ✅ Added 22 new templates: python-3.12, nodejs-20, go-1.22, ...
INFO:     🎉 Template seeding complete! Total templates available: 22
INFO:     ✨ Yantra API ready to serve requests!
```

Or on subsequent startups:

```
INFO:     🚀 Yantra API starting up...
INFO:     📦 Seeding Dockerfile templates...
INFO:     ⏭️  Skipped 22 existing templates
INFO:     🎉 Template seeding complete! Total templates available: 22
INFO:     ✨ Yantra API ready to serve requests!
```

## Troubleshooting

### Templates not appearing in database

1. Check API startup logs for errors
2. Verify database connection in `config.py`
3. Check if `dockerfile_templates` table exists:
```sql
\dt dockerfile_templates
```

### Duplicate key errors

This shouldn't happen due to idempotent checks, but if it does:
- Check for duplicate IDs in `definitions.py`
- Verify the `seed_templates` function is being used (not `update_existing_templates`)

### Import errors

If you see import errors on startup:
- Verify all files are in the `api/templates/` directory
- Check that `__init__.py` exists and exports `seed_templates`
- Ensure `main.py` imports from `templates` correctly
