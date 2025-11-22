import { useState, useEffect } from 'react';
import FileUpload from '../components/FileUpload';
import PipelineViewer from '../components/PipelineViewer';
import { trainModel, previewPipeline, getTrainingStatus } from '../services/api';
import './Model.css';

function Model() {
  const [file, setFile] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [pipelineData, setPipelineData] = useState(null);
  const [trainingStatus, setTrainingStatus] = useState(null);
  const [error, setError] = useState(null);
  const [mode, setMode] = useState('preview'); // 'preview' or 'train'

  useEffect(() => {
    loadTrainingStatus();
  }, []);

  const loadTrainingStatus = async () => {
    try {
      const status = await getTrainingStatus();
      setTrainingStatus(status);
    } catch (err) {
      console.error('Error loading training status:', err);
    }
  };

  const handleFileSelect = async (selectedFile) => {
    setFile(selectedFile);
    setError(null);
    setPipelineData(null);
    setProcessing(true);

    try {
      if (mode === 'preview') {
        const result = await previewPipeline(selectedFile);
        setPipelineData(result);
      } else {
        const result = await trainModel(selectedFile);
        setPipelineData(result);
        await loadTrainingStatus(); // Refresh training status
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Error processing file');
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="model-page">
      <h1>Model Training</h1>
      <p className="page-description">
        Upload individual documents to train the model. The system will detect the content area
        and generate embeddings for the first page of each document.
      </p>

      <div className="mode-selector">
        <button
          className={mode === 'preview' ? 'active' : ''}
          onClick={() => setMode('preview')}
        >
          Preview Pipeline
        </button>
        <button
          className={mode === 'train' ? 'active' : ''}
          onClick={() => setMode('train')}
        >
          Train Model
        </button>
      </div>

      <FileUpload
        onFileSelect={handleFileSelect}
        accept=".pdf"
        label={mode === 'preview' ? 'Preview Document' : 'Upload Training Document'}
      />

      {file && (
        <div className="file-info">
          <p>Selected file: <strong>{file.name}</strong></p>
        </div>
      )}

      {processing && (
        <div className="processing">
          <p>Processing document... This may take a few moments.</p>
        </div>
      )}

      {error && (
        <div className="error">
          <p>Error: {error}</p>
        </div>
      )}

      {pipelineData && (
        <div className="pipeline-results">
          {mode === 'train' && pipelineData.status === 'success' && (
            <div className="success-message">
              <p>✓ Document successfully added to training set!</p>
            </div>
          )}
          <PipelineViewer
            originalImage={pipelineData.original_image}
            croppedImage={pipelineData.cropped_image}
            bbox={pipelineData.bbox}
          />
        </div>
      )}

      {trainingStatus && (
        <div className="training-status">
          <h2>Training Status</h2>
          <p>Number of trained documents: <strong>{trainingStatus.count}</strong></p>
          {trainingStatus.trained_documents.length > 0 && (
            <div className="trained-documents">
              <h3>Trained Documents:</h3>
              <ul>
                {trainingStatus.trained_documents.map((doc, index) => (
                  <li key={index}>{doc}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default Model;

