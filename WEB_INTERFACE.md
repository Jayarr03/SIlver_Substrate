# Silver Substrate Web Interface

Quick setup guide for the web interface.

## Prerequisites

- Python 3.11+
- Node.js 20+
- OpenAI API key

## Setup

### 1. Backend Setup

```bash
# Create/activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and add:
#   OPENAI_API_KEY=your-key-here
#   OPENAI_MODEL=gpt-4o
```

### 2. Frontend Setup

```bash
# Frontend is already initialized in the frontend/ directory
cd frontend
npm install
cd ..
```

## Running the Application

### Option 1: Using Startup Scripts

**Terminal 1 - Backend:**
```bash
./start-backend.sh
```

**Terminal 2 - Frontend:**
```bash
./start-frontend.sh
```

### Option 2: Manual Start

**Terminal 1 - Backend:**
```bash
source .venv/bin/activate
PYTHONPATH=src python3 -m silver_substrate.api
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

## Access the Application

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:5000/api

## Features

### 1. Create New Assessments
- Enter a component name (e.g., "gate oxide", "bond pad")
- Choose interactive mode (AI suggests metadata) or manual mode
- Generate threat assessment with one click
- Assessments saved to `library/` folder

### 2. Browse Library
- View all generated assessments
- See summary, threat count, and requirement count
- Click to view full details

### 3. View Assessment Details
- Comprehensive threat analysis
- Security requirements with SDLC phases
- Prioritized actions
- Export-ready JSON format

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/hardware-levels` - List available hardware levels
- `GET /api/assessments` - List all assessments
- `GET /api/assessments/<filename>` - Get specific assessment
- `POST /api/suggest` - Get AI metadata suggestions
- `POST /api/assess` - Generate new assessment

## Troubleshooting

### Backend won't start
- Ensure Flask is installed: `pip install flask flask-cors`
- Check .env file exists with valid OPENAI_API_KEY
- Verify virtual environment is activated

### Frontend won't start
- Run `npm install` in frontend directory
- Check Node.js version: `node --version` (should be 20+)
- Clear cache: `rm -rf frontend/node_modules && cd frontend && npm install`

### API connection errors
- Ensure backend is running on port 5000
- Check CORS is enabled in api.py
- Verify frontend is making requests to http://localhost:5000/api
