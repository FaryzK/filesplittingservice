import { useState } from 'react';
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
  const [pageNumber, setPageNumber] = useState(1);

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
          <div className="pdf-navigation">
            <button
              onClick={() => setPageNumber((prev) => Math.max(1, prev - 1))}
              disabled={pageNumber <= 1}
            >
              Previous
            </button>
            <span>
              Page {pageNumber} of {numPages || '--'}
            </span>
            <button
              onClick={() => setPageNumber((prev) => Math.min(numPages || 1, prev + 1))}
              disabled={pageNumber >= (numPages || 1)}
            >
              Next
            </button>
          </div>
          <div className="pdf-viewer">
            <Document
              file={downloadFile(filename)}
              onLoadSuccess={onDocumentLoadSuccess}
              loading={<div>Loading PDF...</div>}
            >
              <Page pageNumber={pageNumber} width={800} />
            </Document>
          </div>
        </div>
      </div>
    </div>
  );
}

export default PDFPreview;

