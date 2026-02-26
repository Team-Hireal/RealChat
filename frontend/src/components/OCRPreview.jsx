import { useState, useEffect } from 'react';
import './OCRPreview.css';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5050';

const OCRPreview = () => {
  const [imageUrl, setImageUrl] = useState('');
  const [error, setError] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(Date.now());

  useEffect(() => {
    // Refresh image every 1 second
    const interval = setInterval(() => {
      setLastUpdate(Date.now());
      setError(false);
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const handleImageError = () => {
    setError(true);
  };

  const handleImageLoad = () => {
    setError(false);
  };

  return (
    <div className="ocr-preview">
      <h3 className="ocr-preview-title">OCR Live Preview</h3>
      <div className="ocr-preview-container">
        {error ? (
          <div className="ocr-preview-placeholder">
            <span>📷</span>
            <p>No OCR capture available</p>
            <small>OCR will capture when reading messages</small>
          </div>
        ) : (
          <img
            src={`${API_BASE}/api/wechat/ocr-debug-image?t=${lastUpdate}`}
            alt="OCR Debug Preview"
            className="ocr-preview-image"
            onError={handleImageError}
            onLoad={handleImageLoad}
          />
        )}
      </div>
      <div className="ocr-preview-info">
        <small>Updates every second • Shows captured message area</small>
      </div>
    </div>
  );
};

export default OCRPreview;
