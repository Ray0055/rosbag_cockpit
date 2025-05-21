# Rosbag Cockpit

A full-stack application for managing, visualizing, and testing rosbag files with a Python backend and Vue.js frontend.

## Project Overview

rosbag Cockpit is a comprehensive web application designed to visualize and manage rosbag files in a user-friendly interface. The application consists of two main components:

1. **Backend**: Python-based API for rosbag file processing and data management
2. **Frontend**: Vue.js web interface for data visualization and interaction

## Key Features

- **rosbag Visualization**: A web interface to view and manage all rosbag files
- **Metadata Explorer**: Browse through topics and metadata of each rosbag file
- **CI/CD Integration**: Execute open-loop tests in continuous integration pipelines
- **Database Management**: Store and query rosbag metadata efficiently

## Backend Architecture

The backend is structured as a Python application with the following components:

### Directory Structure

```
backend/
├── .pytest_cache/
├── bag_processor/
│   ├── api/
│   │   ├── logs/
│   │   ├── __init__.py
│   │   ├── exception_handlers.py
│   │   ├── logging.py
│   │   ├── models.py
│   │   ├── routes.py
│   │   ├── schema.py
│   │   ├── services.py
│   │   └── utils.py
│   ├── bag_manager/
│   │   ├── __init__.py
│   │   ├── error.py
│   │   ├── parser.py
│   │   ├── player.py
│   │   └── utils.py
│   └── database/
│       ├── __init__.py
│       ├── db_connection_pool.py
│       ├── db_initializer.py
│       ├── models.py
│       ├── operations.py
│       └── schema.py
├── test/
│   ├── __init__.py
│   └── script_used_in_ci_cd.py
├── .gitignore
└── ...
```

### Key Components

#### API Module (`bag_processor/api`)

- `routes.py`: API endpoints for rosbag operations
- `services.py`: Business logic for processing requests
- `models.py`: Data models for rosbag metadata
- `schema.py`: Validation schemas for API requests/responses
- `exception_handlers.py`: Custom exception handling
- `logging.py`: Logging configuration

#### Bag Manager (`bag_processor/bag_manager`)

- `parser.py`: rosbag file parsing functionality
- `player.py`: Controls playback of rosbag data
- `error.py`: Custom error handling for bag operations
- `utils.py`: Utility functions for bag management

#### Database Module (`bag_processor/database`)

- `db_connection_pool.py`: Database connection pooling
- `db_initializer.py`: Database initialization scripts
- `models.py`: ORM models for database entities
- `operations.py`: Database CRUD operations
- `schema.py`: Database schema definitions

### Tech Stack

- **Framework**: FastAPI or Flask (based on project structure)
- **Database**: SQL database (specific type not specified in structure)
- **Testing**: pytest

## Frontend Architecture

The frontend is a Vue.js application with the following structure:

### Directory Structure

```
frontend/
├── .vscode/
├── node_modules/
├── public/
├── src/
│   ├── assets/
│   ├── components/
│   │   ├── Dashboard.vue
│   │   ├── DataTable.vue
│   │   ├── NavBar.vue
│   │   └── RosbagDetail.vue
│   ├── services/
│   │   ├── api.js
│   │   └── rosbagService.js
│   └── views/
│       ├── App.vue
│       ├── DatabaseView.vue
│       ├── HomeView.vue
│       └── main.js
└── ...
```

### Key Components

#### Views

- `HomeView.vue`: Main landing page
- `DatabaseView.vue`: Database interaction view
- `App.vue`: Root application component

#### Components

- `Dashboard.vue`: Overview dashboard for rosbag data
- `DataTable.vue`: Data table component for displaying rosbag contents
- `NavBar.vue`: Navigation bar component
- `RosbagDetail.vue`: Detailed view of rosbag files

#### Services

- `api.js`: API communication service
- `rosbagService.js`: rosbag-specific API methods

### Tech Stack

- **Framework**: Vue.js
- **Styling**: Tailwind CSS
- **Build Tool**: Vite

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- Docker and Docker Compose

### Backend Setup

Please follow the readme in the backend directory: [readme](backend/README.md)

### Frontend Setup

Please follow the readme in the frontend directory: [readme](frontend/README.md)

### Docker Deployment

The project includes Docker configuration for containerized deployment:

1. Build and start the containers:
   ```bash
   source start.sh
   ```
2. Access the application at `http://localhost:8000` for the backend and `http://localhost:5173` for the frontend.

## Usage

### rosbag Management

1. Create rosbag_database using the command:
   ```bash
   uv run main.py --db /path/to/your/db --dir /path/to/your/rosbags/
   ```
2. View all available rosbag files in the dashboard
3. Explore topics and metadata for each rosbag file
4. Filter and search through rosbag files based on metadata

### Open-Loop Testing

1. Select rosbag files for testing
2. Configure test parameters
3. Execute open-loop tests
4. View test results and reports
5. Integrate with CI/CD pipelines for automated testing
