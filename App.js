import React, { useState } from 'react';
import './App.css';

function App() {
  const [image, setImage] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleImageChange = (e) => {
    setImage(e.target.files[0]);
    setError(null);
    setResult(null);
  };

  const handleUpload = async () => {
    if (!image) {
      setError('Please select an image first!');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', image);

      console.log('Sending request to backend...');
      
      // Use backend service name from docker-compose
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
        headers: {
          'Accept': 'application/json',
        },
      });

      console.log('Response received:', response.status);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Data received from backend');

      if (data.error) {
        throw new Error(data.error);
      }

      setResult(`data:image/jpeg;base64,${data.image}`);
      console.log('Image set successfully');
    } catch (error) {
      console.error('Upload error:', error);
      setError(`Error uploading image: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <h1>YOLO Object Detection</h1>
      <div className="upload-section">
        <input 
          type="file" 
          onChange={handleImageChange} 
          accept="image/*" 
          disabled={loading}
        />
        <button 
          onClick={handleUpload} 
          disabled={!image || loading}
        >
          {loading ? 'Processing...' : 'Upload and Detect'}
        </button>
      </div>

      {error && <div className="error">{error}</div>}
      
      {result && (
        <div className="result">
          <img src={result} alt="Detection Result" />
        </div>
      )}
    </div>
  );
}

export default App;