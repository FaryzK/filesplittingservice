# PDF Document Splitter MVP

An automated system for splitting composite PDF documents into individual files using image and text embeddings.

## Features

- **Training Pipeline**: Upload individual documents to train the model
  - Automatic content area detection (handles IC cards and forms positioned anywhere on A4)
  - Image embedding generation using CLIP-ViT-L-14
  - Text embedding generation using OpenAI text-embedding-3-small
  - Pipeline visualization

- **Inference Pipeline**: Upload composite PDFs to automatically split them
  - Page-by-page content detection and embedding generation
  - Similarity matching with training set (threshold > 0.85)
  - Automatic document splitting at identified boundaries
  - PDF preview and download functionality

## Project Structure

```
FileSplit/
├── backend/              # Python FastAPI backend
│   ├── main.py          # FastAPI application
│   ├── pdf_processor.py # PDF to image/text conversion
│   ├── content_detector.py # OpenCV content area detection
│   ├── embeddings.py    # Image and text embedding generation
│   ├── training.py      # Training pipeline
│   ├── inference.py     # Inference pipeline
│   ├── utils.py         # Utility functions
│   ├── data/            # Embeddings storage (JSON)
│   ├── uploads/         # Temporary upload storage
│   └── outputs/         # Split document outputs
├── frontend/            # React + Vite frontend
│   └── src/
│       ├── pages/       # Inference and Model screens
│       ├── components/  # Reusable components
│       └── services/    # API client
└── sample/              # Sample PDF files for testing
```

## Setup

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# Copy .env.example to .env and add your OpenAI API key
cp .env.example .env
# Edit .env and add: OPENAI_API_KEY=your_key_here
```

5. Run the backend server:
```bash
python main.py
# Or: uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Usage

### Training the Model

1. Navigate to the **Model** screen in the frontend
2. Click "Upload Training Document"
3. Select an individual PDF document (e.g., from the `sample/` folder)
4. The system will:
   - Detect the content area on the first page
   - Generate image and text embeddings
   - Store the embeddings for future matching

### Running Inference

1. Navigate to the **Inference** screen in the frontend
2. Click "Upload Composite PDF"
3. Select a composite PDF document (e.g., `sample/final_combined_all.pdf`)
4. The system will:
   - Process each page
   - Compare embeddings with the training set
   - Identify first pages (similarity > 0.85)
   - Split the document at identified boundaries
5. Preview or download the split documents

## Requirements

### Backend
- Python 3.8+
- OpenAI API key (for text embeddings)
- Poppler (for pdf2image) - Install separately:
  - Windows: Download from [poppler-windows](https://github.com/oschwartz10612/poppler-windows/releases)
  - macOS: `brew install poppler`
  - Linux: `sudo apt-get install poppler-utils`

**Note**: The Poppler path is configured in `backend/pdf_processor.py` (line 10). If your Poppler is installed in a different location, update the `POPPLER_PATH` variable. Alternatively, you can add Poppler's `bin` folder to your system PATH.

### Frontend
- Node.js 18+
- npm or yarn

## Configuration

- **Similarity Threshold**: 0.85 (configurable in `backend/inference.py`)
- **Content Detection**: OpenCV contour detection with 5% minimum area ratio
- **Embedding Models**:
  - Image: CLIP-ViT-L-14 (via sentence-transformers)
  - Text: OpenAI text-embedding-3-small

## Notes

- The system stores embeddings locally in JSON format (no database required)
- Uploaded files are temporarily stored in `backend/uploads/`
- Split documents are saved in `backend/outputs/`
- The first page of each document is used for matching

