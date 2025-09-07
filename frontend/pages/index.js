import { useState, useRef } from 'react';
import Head from 'next/head';

export default function Home() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [maxPages, setMaxPages] = useState('');
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);

  // Get backend URL from environment variable (secure!)
  const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8080';

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      const validTypes = ['application/pdf', 'text/plain', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
      if (validTypes.includes(file.type)) {
        setSelectedFile(file);
        setError('');
      } else {
        setError('Please select a PDF, TXT, or DOCX file');
        setSelectedFile(null);
      }
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a document file');
      return;
    }

    setIsProcessing(true);
    setError('');

    const formData = new FormData();
    formData.append('file', selectedFile);
    if (maxPages) {
      formData.append('max_pages', maxPages);
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/upload`, {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${selectedFile.name.split('.')[0]}_converted.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        // Reset form
        setSelectedFile(null);
        setMaxPages('');
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Processing failed. Please try again.');
      }
    } catch (err) {
      setError('Network error. Please check your connection and try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const resetSelection = () => {
    setSelectedFile(null);
    setMaxPages('');
    setError('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <>
      <Head>
        <title>DoxTract - Professional Document Extraction</title>
        <meta name="description" content="Convert PDF, TXT, and DOCX files to structured JSON format" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
        <link rel="icon" href="/icon.svg" type="image/svg+xml" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
        <meta name="theme-color" content="#2563eb" />
        <link rel="manifest" href="/manifest.json" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet" />
      </Head>

      <div className="app">
        {/* Header */}
        <header className="header">
          <div className="container">
            <div className="logo">
              <i className="fas fa-file-alt"></i>
              <span>DoxTract</span>
            </div>
            <nav className="nav">
              <a href="https://github.com/Shreyas-prog108/doxtract" target="_blank" rel="noopener noreferrer">Features</a>
              <a href="https://github.com/Shreyas-prog108/doxtract" target="_blank" rel="noopener noreferrer">API Docs</a>
              <a href="https://x.com/Shreyas_Pandeyy" target="_blank" rel="noopener noreferrer">Support</a>
            </nav>
          </div>
        </header>

        {/* Hero Section */}
        <section className="hero">
          <div className="container">
            <div className="hero-content">
              <h1>Professional Document Extraction</h1>
              <p>Convert PDF, TXT, and DOCX files to structured JSON format with enterprise-grade accuracy</p>
              
              {/* Upload Section */}
              <div className="upload-section">
                <div className="upload-area">
                  <input
                    type="file"
                    ref={fileInputRef}
                    onChange={handleFileSelect}
                    accept=".pdf,.txt,.docx"
                    className="file-input"
                  />
                  <div className="upload-content">
                    <i className="fas fa-cloud-upload-alt"></i>
                    <h3>Choose Document</h3>
                    <p>PDF, TXT, or DOCX files (max 50MB)</p>
                  </div>
                </div>

                {selectedFile && (
                  <div className="file-info">
                    <div className="file-details">
                      <i className="fas fa-file"></i>
                      <span>{selectedFile.name}</span>
                      <span className="file-size">({(selectedFile.size / 1024 / 1024).toFixed(1)} MB)</span>
                    </div>
                    <button onClick={resetSelection} className="reset-btn">
                      <i className="fas fa-times"></i>
                    </button>
                  </div>
                )}

                <div className="options">
                  <label>
                    Max Pages (optional):
                    <input
                      type="number"
                      value={maxPages}
                      onChange={(e) => setMaxPages(e.target.value)}
                      placeholder="Leave empty to process all pages"
                      min="1"
                      className="option-input"
                    />
                  </label>
                </div>

                <button
                  onClick={handleUpload}
                  disabled={!selectedFile || isProcessing}
                  className="convert-btn"
                >
                  {isProcessing ? (
                    <>
                      <i className="fas fa-spinner fa-spin"></i>
                      Processing...
                    </>
                  ) : (
                    <>
                      <i className="fas fa-magic"></i>
                      Extract to JSON
                    </>
                  )}
                </button>

                {error && (
                  <div className="error-message">
                    <i className="fas fa-exclamation-triangle"></i>
                    {error}
                  </div>
                )}
              </div>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="footer">
          <div className="container">
            <div className="footer-content">
              <div className="footer-section">
                <h4>DoxTract</h4>
                <p>Professional document processing service</p>
              </div>
              <div className="footer-section">
                <h4>Resources</h4>
                <a href="https://github.com/Shreyas-prog108/doxtract" target="_blank" rel="noopener noreferrer">API Documentation</a>
                <a href="https://x.com/Shreyas_Pandeyy" target="_blank" rel="noopener noreferrer">Support</a>
              </div>
            </div>
            <div className="footer-bottom">
              <p>&copy; 2025 DoxTract. Built for document processing needs.</p>
            </div>
          </div>
        </footer>
      </div>
    </>
  );
}
