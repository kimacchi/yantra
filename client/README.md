# Yantra Client

React web application for managing Yantra compiler images.

## Features

- **View Compilers** - Browse all runtime environments with real-time status updates
- **Create Compilers** - Define new compilers with custom Dockerfiles
- **Edit Compilers** - Update existing compiler configurations
- **Delete Compilers** - Remove compilers and cleanup Docker images
- **Monaco Editor** - VSCode-quality Dockerfile editing with syntax highlighting
- **Auto-refresh** - Status updates every 5 seconds
- **Dark Theme** - Beautiful dark UI built with Tailwind CSS

## Tech Stack

- React 18 + TypeScript
- Vite (build tool)
- React Router (navigation)
- Monaco Editor (code editor)
- Tailwind CSS (styling)
- Axios (API client)

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Yantra API running on http://localhost:8000

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at **http://localhost:3000**

### Build for Production

```bash
npm run build
```

## API Configuration

The app proxies API requests to `http://localhost:8000`. To change the API URL, edit `vite.config.ts`:

```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://your-api-url:8000',
      // ...
    }
  }
}
```

## Project Structure

```
src/
├── api/            # API client functions
├── components/     # Reusable UI components
├── pages/          # Page components with routes
├── types/          # TypeScript interfaces
├── App.tsx         # Root component with routing
├── main.tsx        # Entry point
└── index.css       # Global styles with Tailwind
```

## Usage

### Creating a Compiler

1. Click "New Compiler" in the navigation
2. Fill in the form:
   - **ID**: Unique identifier (e.g., `python-3.11`)
   - **Name**: Display name (e.g., `Python 3.11`)
   - **Dockerfile**: Write your Dockerfile in the Monaco editor
   - **Run Command**: JSON array like `["python", "-"]`
   - **Resources**: Memory, CPU, and timeout limits
3. Click "Create Compiler"
4. The worker will build the Docker image automatically

### Editing a Compiler

1. Click "Edit" on any compiler card
2. Modify the fields
3. Click "Update Compiler"
4. If Dockerfile changes, a rebuild will be triggered

### Monitoring Build Status

- Status badges show: Pending (yellow), Building (blue), Ready (green), Failed (red)
- The list auto-refreshes every 5 seconds
- Click "Rebuild" to manually trigger a build

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

### Code Style

The project uses TypeScript strict mode and includes:
- Type safety with interfaces
- ESLint configuration
- React best practices
