import { useRef } from 'react';
import './FileUpload.css';

function FileUpload({ onFileSelect, accept = '.pdf', label = 'Upload PDF', disabled = false }) {
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && !disabled) {
      onFileSelect(file);
    }
  };

  const handleClick = () => {
    if (!disabled) {
      fileInputRef.current?.click();
    }
  };

  return (
    <div className="file-upload">
      <input
        ref={fileInputRef}
        type="file"
        accept={accept}
        onChange={handleFileChange}
        style={{ display: 'none' }}
        disabled={disabled}
      />
      <button onClick={handleClick} className="upload-button" disabled={disabled}>
        {label}
      </button>
    </div>
  );
}

export default FileUpload;

