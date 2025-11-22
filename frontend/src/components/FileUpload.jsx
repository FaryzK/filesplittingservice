import { useRef } from 'react';
import './FileUpload.css';

function FileUpload({ onFileSelect, accept = '.pdf', label = 'Upload PDF' }) {
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      onFileSelect(file);
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="file-upload">
      <input
        ref={fileInputRef}
        type="file"
        accept={accept}
        onChange={handleFileChange}
        style={{ display: 'none' }}
      />
      <button onClick={handleClick} className="upload-button">
        {label}
      </button>
    </div>
  );
}

export default FileUpload;

