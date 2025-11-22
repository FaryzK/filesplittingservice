import { useState, useEffect } from 'react';
import FileUpload from '../components/FileUpload';
import PDFPreview from '../components/PDFPreview';
import { runInference, downloadFile, getInferenceProgress } from '../services/api';
import './Inference.css';

function Inference() {
  const [file, setFile] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [splitDocuments, setSplitDocuments] = useState([]);
  const [error, setError] = useState(null);
  const [previewFile, setPreviewFile] = useState(null);
  const [progress, setProgress] = useState(null);
  const [jobId, setJobId] = useState(null);

  useEffect(() => {
    let intervalId = null;
    
    if (jobId && processing) {
      // Poll for progress updates
      const pollProgress = async () => {
        try {
          const progressData = await getInferenceProgress(jobId);
          console.log('Progress data:', progressData); // Debug log
          setProgress(progressData);
          
          if (progressData.status === 'completed') {
            setProcessing(false);
            setSplitDocuments(progressData.result?.split_documents || []);
            setProgress(null);
            setJobId(null);
            if (intervalId) {
              clearInterval(intervalId);
            }
          } else if (progressData.status === 'failed') {
            setProcessing(false);
            setError(progressData.error || 'Processing failed');
            setProgress(null);
            setJobId(null);
            if (intervalId) {
              clearInterval(intervalId);
            }
          }
        } catch (err) {
          console.error('Error fetching progress:', err);
          // Don't stop polling on error, might be temporary
        }
      };
      
      // Poll immediately, then set interval
      pollProgress();
      intervalId = setInterval(pollProgress, 500); // Poll every 500ms
    }
    
    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [jobId, processing]);

  const handleFileSelect = async (selectedFile) => {
    setFile(selectedFile);
    setError(null);
    setSplitDocuments([]);
    setProgress(null);
    setProcessing(true);

    try {
      const result = await runInference(selectedFile);
      setJobId(result.job_id);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Error processing file');
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
      <div className="page-header">
        <h1>Document Splitter</h1>
        <p className="page-description">
          Upload a document to automatically split it into individual documents.
        </p>
      </div>

      <div className="upload-section">
        <FileUpload
          onFileSelect={handleFileSelect}
          accept=".pdf"
          label="Upload File"
          disabled={processing}
        />
      </div>

      {file && !processing && (
        <div className="file-info">
          <div className="file-info-content">
            <svg className="file-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <div>
              <p className="file-name">{file.name}</p>
              <p className="file-status">Ready for processing</p>
            </div>
          </div>
        </div>
      )}

      {processing && progress && (
        <div className="processing-container">
          <div className="processing-header">
            <div className="processing-icon">
              <div className="spinner"></div>
            </div>
            <div className="processing-info">
              <h3>{progress.message}</h3>
              <p className="processing-status">{progress.status}</p>
            </div>
          </div>

          <div className="progress-bar-container">
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${progress.progress_percentage}%` }}
              ></div>
            </div>
            <div className="progress-text">
              {progress.current_page > 0 && progress.total_pages > 0 ? (
                <span>Page {progress.current_page} of {progress.total_pages}</span>
              ) : (
                <span>{progress.progress_percentage}%</span>
              )}
            </div>
          </div>

          {progress.processed_pages && progress.processed_pages.length > 0 && (
            <div className="pages-preview">
              <h4>Pages Analyzed</h4>
              <div className="pages-grid">
                {progress.processed_pages.map((page, idx) => (
                  <div 
                    key={idx} 
                    className={`page-indicator ${page.matched ? 'matched' : ''}`}
                    title={page.matched ? `Matched: ${page.best_match}` : 'No match'}
                  >
                    <span className="page-number">{page.page}</span>
                    {page.matched && <span className="match-badge">✓</span>}
                  </div>
                ))}
              </div>
            </div>
          )}

          {progress.identified_documents && progress.identified_documents.length > 0 && (
            <div className="identified-documents">
              <h4>Documents Identified</h4>
              <div className="documents-list">
                {progress.identified_documents.map((doc, idx) => (
                  <div key={idx} className="identified-doc-item">
                    <div className="doc-icon">📄</div>
                    <div className="doc-info">
                      <p className="doc-name">Document {idx + 1}</p>
                      <p className="doc-details">
                        Page {doc.page} • {doc.matched_document}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {error && (
        <div className="error-container">
          <div className="error-icon">⚠️</div>
          <div className="error-content">
            <h3>Error</h3>
            <p>{error}</p>
          </div>
        </div>
      )}

      {splitDocuments.length > 0 && !processing && (
        <div className="results-container">
          <div className="results-header">
            <h2>Split Documents</h2>
            <span className="results-count">{splitDocuments.length} document{splitDocuments.length !== 1 ? 's' : ''}</span>
          </div>
          <div className="document-grid">
            {splitDocuments.map((doc, index) => (
              <div key={index} className="document-card">
                <div className="document-card-header">
                  <div className="document-icon">📑</div>
                  <div className="document-title">
                    <h3>{doc.filename}</h3>
                    <p className="document-pages">Pages {doc.start_page} - {doc.end_page}</p>
                  </div>
                </div>
                <div className="document-card-actions">
                  <button
                    onClick={() => handlePreview(doc.filename)}
                    className="action-btn preview-btn"
                  >
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                    Preview
                  </button>
                  <button
                    onClick={() => handleDownload(doc.filename)}
                    className="action-btn download-btn"
                  >
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
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
