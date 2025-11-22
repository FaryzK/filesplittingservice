import './PipelineViewer.css';

function PipelineViewer({ originalImage, croppedImage, bbox }) {
  return (
    <div className="pipeline-viewer">
      <h3>Content Detection Pipeline</h3>
      <div className="pipeline-steps">
        <div className="pipeline-step">
          <h4>Original First Page</h4>
          {originalImage && (
            <img src={originalImage} alt="Original" className="pipeline-image" />
          )}
        </div>
        <div className="pipeline-step">
          <h4>Detected Content Area</h4>
          {bbox && (
            <div className="bbox-info">
              <p>Bounding Box: ({bbox[0]}, {bbox[1]})</p>
              <p>Size: {bbox[2]} × {bbox[3]} pixels</p>
            </div>
          )}
        </div>
        <div className="pipeline-step">
          <h4>Cropped Content</h4>
          {croppedImage && (
            <img src={croppedImage} alt="Cropped" className="pipeline-image" />
          )}
        </div>
      </div>
    </div>
  );
}

export default PipelineViewer;

