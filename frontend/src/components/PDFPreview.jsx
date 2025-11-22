import { useState, useEffect } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import { downloadFile } from '../services/api';
import './PDFPreview.css';

// Set up PDF.js worker
if (typeof window !== 'undefined') {
  pdfjs.GlobalWorkerOptions.workerSrc = new URL(
    'pdfjs-dist/build/pdf.worker.min.js',
    import.meta.url,
  ).toString();
}

function PDFPreview({ filename, onClose }) {
  const [numPages, setNumPages] = useState(null);

  // Handle ESC key to close preview
  useEffect(() => {
    const handleEscKey = (event) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };

    // Add event listener when component mounts
    window.addEventListener('keydown', handleEscKey);

    // Cleanup: remove event listener when component unmounts
    return () => {
      window.removeEventListener('keydown', handleEscKey);
    };
  }, [onClose]);

  function onDocumentLoadSuccess({ numPages }) {
    setNumPages(numPages);
  }

  const handleDownload = () => {
    window.open(downloadFile(filename), '_blank');
  };

  return (
    <div className="pdf-preview-overlay" onClick={onClose}>
      <div className="pdf-preview-container" onClick={(e) => e.stopPropagation()}>
        <div className="pdf-preview-header">
          <h3>{filename}</h3>
          <div className="pdf-preview-controls">
            <button onClick={handleDownload} className="download-btn">
              Download
            </button>
            <button onClick={onClose} className="close-btn">
              Close
            </button>
          </div>
        </div>
        <div className="pdf-preview-content">
          {numPages && (
            <div className="pdf-page-info">
              <span>{numPages} page{numPages !== 1 ? 's' : ''}</span>
            </div>
          )}
          <div className="pdf-viewer">
            <Document
              file={downloadFile(filename)}
              onLoadSuccess={onDocumentLoadSuccess}
              loading={<div>Loading PDF...</div>}
              options={{
                cMapUrl: 'https://unpkg.com/pdfjs-dist@3.11.174/cmaps/',
                cMapPacked: true,
              }}
            >
              {numPages && Array.from(new Array(numPages), (el, index) => (
                <div key={`page_wrapper_${index + 1}`} className="pdf-page-wrapper">
                  <Page
                    key={`page_${index + 1}`}
                    pageNumber={index + 1}
                    width={800}
                    renderTextLayer={true}
                    renderAnnotationLayer={true}
                    className="pdf-page"
                  />
                </div>
              ))}
            </Document>
          </div>
        </div>
      </div>
    </div>
  );
}

export default PDFPreview;

