# Quick Start Guide

## Prerequisites

1. **Python 3.8+** installed
2. **Node.js 18+** installed
3. **OpenAI API Key** (for text embeddings)
4. **Poppler** installed (for PDF to image conversion)
   - Windows: Download from [poppler-windows](https://github.com/oschwartz10612/poppler-windows/releases) and add to PATH
   - macOS: `brew install poppler`
   - Linux: `sudo apt-get install poppler-utils`

## Setup Steps

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Create .env file with:
OPENAI_API_KEY=your_openai_api_key_here
```

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

## Running the Application

### Start Backend Server

```bash
# From backend directory
python main.py

# Or use the startup script
# Windows:
start_server.bat
# macOS/Linux:
./start_server.sh
```

Backend will run on `http://localhost:8000`

### Start Frontend Server

```bash
# From frontend directory
npm run dev
```

Frontend will run on `http://localhost:5173`

## Usage Workflow

### Step 1: Train the Model

1. Open the frontend at `http://localhost:5173`
2. Navigate to the **Model** tab
3. Click "Upload Training Document"
4. Select an individual PDF from the `sample/` folder (e.g., `uk_passport.pdf`)
5. Click "Train Model" to save embeddings
6. Repeat for all document types you want to recognize

### Step 2: Run Inference

1. Navigate to the **Inference** tab
2. Click "Upload Composite PDF"
3. Select a composite PDF (e.g., `sample/final_combined_all.pdf`)
4. Wait for processing
5. View, preview, or download the split documents

## Troubleshooting

### Backend Issues

- **Import errors**: Make sure you're running from the backend directory or have added it to PYTHONPATH
- **OpenAI API errors**: Check that your API key is set in `.env` file
- **Poppler errors**: Ensure Poppler is installed and in your system PATH

### Frontend Issues

- **CORS errors**: Make sure backend is running on port 8000
- **PDF preview not working**: Check browser console for errors, may need to install pdfjs-dist

### Common Issues

- **No matches found**: Make sure you've trained the model with at least one document
- **Low similarity scores**: Try training with clearer document images
- **Content detection issues**: Adjust `min_area_ratio` in `content_detector.py` if needed

