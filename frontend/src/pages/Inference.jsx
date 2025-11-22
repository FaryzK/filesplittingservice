import { useState } from 'react';
import FileUpload from '../components/FileUpload';
import PDFPreview from '../components/PDFPreview';
import { runInference, downloadFile } from '../services/api';
import './Inference.css';

function Inference() {
  const [file, setFile] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [splitDocuments, setSplitDocuments] = useState([]);
  const [error, setError] = useState(null);
  const [previewFile, setPreviewFile] = useState(null);

  const handleFileSelect = async (selectedFile) => {
    setFile(selectedFile);
    setError(null);
    setSplitDocuments([]);
    setProcessing(true);

    try {
      const result = await runInference(selectedFile);
      setSplitDocuments(result.split_documents || []);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Error processing file');
    } finally {
      setProcessing(false);
    }
  };

  const handlePreview = (filename) => {
    setPreviewFile(filename);
  };

  const handleDownload = (filename) => {
    window.open(downloadFile(filename), '_blank');
  };

  return (
    <div className="inference-page">
      <h1>Document Splitting (Inference)</h1>
      <p className="page-description">
        Upload a composite PDF document to automatically split it into individual documents.
      </p>

      <FileUpload
        onFileSelect={handleFileSelect}
        accept=".pdf"
        label="Upload Composite PDF"
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

      {splitDocuments.length > 0 && (
        <div className="results">
          <h2>Split Documents ({splitDocuments.length})</h2>
          <div className="document-list">
            {splitDocuments.map((doc, index) => (
              <div key={index} className="document-item">
                <div className="document-info">
                  <h3>{doc.filename}</h3>
                  <p>Pages: {doc.start_page} - {doc.end_page}</p>
                </div>
                <div className="document-actions">
                  <button
                    onClick={() => handlePreview(doc.filename)}
                    className="preview-btn"
                  >
                    Preview
                  </button>
                  <button
                    onClick={() => handleDownload(doc.filename)}
                    className="download-btn"
                  >
                    Download
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {previewFile && (
        <PDFPreview
          filename={previewFile}
          onClose={() => setPreviewFile(null)}
        />
      )}
    </div>
  );
}

export default Inference;

