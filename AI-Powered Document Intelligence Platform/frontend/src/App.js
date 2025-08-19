import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [files, setFiles] = useState([]);
  const [query, setQuery] = useState('');
  
  const [response, setResponse] = useState('');
  const [uploading, setUploading] = useState(false);
  const [asking, setAsking] = useState(false);

  const handleFileChange = (e) => {
    setFiles(e.target.files);
  };

  const handleUpload = async () => {
    if (files.length === 0) {
      alert('Please select files to upload');
      return;
    }
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }
    setUploading(true);
    try {
      await axios.post('http://127.0.0.1:5000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      alert('Files uploaded successfully');
    } catch (error) {
      console.error('Error uploading files:', error);
      alert('Error uploading files');
    }
    setUploading(false);
  };

  const handleAsk = async () => {
    if (!query) {
      alert('Please enter a query');
      return;
    }
    setAsking(true);
    try {
      const result = await axios.post('http://127.0.0.1:5000/ask', { query });
      setResponse(result.data.response);
    } catch (error) {
      console.error('Error asking question:', error);
      alert('Error asking question');
    }
    setAsking(false);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>AI-Powered Document Intelligence Platform</h1>
        <div className="card">
          <h2>Upload Documents</h2>
          <input type="file" multiple onChange={handleFileChange} />
          <button onClick={handleUpload} disabled={uploading}>
            {uploading ? 'Uploading...' : 'Upload'}
          </button>
        </div>
        <div className="card">
          <h2>Ask a Question</h2>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter your question"
          />
          <button onClick={handleAsk} disabled={asking}>
            {asking ? 'Asking...' : 'Ask'}
          </button>
          {response && (
            <div className="response">
              <h3>Response:</h3>
              <p>{response}</p>
            </div>
          )}
        </div>
      </header>
    </div>
  );
}

export default App;
