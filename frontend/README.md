
# Frontend Project Setup

## Installation and Running the Project

### Method 1: Command Line

```bash
# Navigate to the frontend directory
cd path/to/frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

### Method 2: Using VSCode

1. Open the project in VSCode
2. Add the following configuration to your `.vscode/launch.json` file:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "type": "node",
            "request": "launch",
            "name": "Start Frontend Development Server",
            "runtimeExecutable": "npm",
            "runtimeArgs": [
                "run",
                "dev"
            ]
        }
    ]
}
```

3. Press F5 or click the "Run and Debug" button to start the development server

## Notes

- Make sure you have Node.js and npm installed on your system
- The development server typically runs on `http://localhost:5173` (for Vite) or `http://localhost:8080` (for Vue CLI)
