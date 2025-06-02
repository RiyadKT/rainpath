import { useState } from 'react';
import Head from '../new-scanner/node_modules/next/head';

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [analysis, setAnalysis] = useState(null);

  const handleFileChange = (e) => {
    if (e.target.files.length > 0) {
      setSelectedFile(e.target.files[0]);
      setAnalysis(null);
    }
  };

  const analyzeDocument = async () => {
    if (!selectedFile) return;

    setLoading(true);
    
    // Create a FormData object to send the file
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      // Call our Python API endpoint
      const response = await fetch('http://localhost:5006/analyze', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('API request failed');
      }

      const data = await response.json();
      setAnalysis(data);
    } catch (error) {
      console.error('Error analyzing document:', error);
      setAnalysis({ error: 'Failed to analyze document. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <Head>
        <title>Patient Document Scanner</title>
        <meta name="description" content="Analyze patient medical documents using OpenAI Vision API" />
      </Head>

      <main>
        <h1>Patient Document Scanner</h1>
        
        <div className="upload-section">
          <input
            type="file"
            accept=".jpg,.jpeg,.png,.pdf"
            onChange={handleFileChange}
            disabled={loading}
          />
          
          <button 
            onClick={analyzeDocument} 
            disabled={!selectedFile || loading}
            className="analyze-btn"
          >
            {loading ? 'Analyzing...' : 'Analyze Document'}
          </button>
        </div>

        {selectedFile && (
          <div className="file-preview">
            <h2>Image Preview</h2>
            <img 
              src={URL.createObjectURL(selectedFile)} 
              alt="Selected file preview" 
              className="preview-image"
            />
          </div>
        )}

        {analysis && (
          <div className="results">
            <h2>Analysis Results</h2>
            {analysis.error ? (
              <p className="error">{analysis.error}</p>
            ) : (
              <div className="parsed-output">
                {Object.entries(analysis).map(([key, value]) => (
                  <div key={key} className="output-item">
                    <strong>{key.replace(/_/g, ' ')}:</strong> {typeof value === 'object' ? JSON.stringify(value, null, 2) : value}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </main>

      <style jsx>{`
        .container {
          min-height: 100vh;
          padding: 0 2rem;
          display: flex;
          flex-direction: column;
          justify-content: center;
          align-items: center;
        }

        main {
          padding: 4rem 0;
          flex: 1;
          display: flex;
          flex-direction: column;
          justify-content: center;
          align-items: center;
          width: 100%;
          max-width: 800px;
        }

        h1 {
          margin-bottom: 2rem;
        }

        .upload-section {
          display: flex;
          flex-direction: column;
          gap: 1rem;
          width: 100%;
          margin-bottom: 1rem;
        }

        .analyze-btn {
          padding: 0.5rem 1rem;
          background-color: #0070f3;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 1rem;
        }

        .analyze-btn:disabled {
          background-color: #cccccc;
          cursor: not-allowed;
        }

        .file-info {
          margin: 1rem 0;
        }

        .file-preview {
          margin-top: 2rem;
          text-align: center;
        }

        .preview-image {
          max-width: 100%;
          max-height: 400px;
          border: 1px solid #eaeaea;
          border-radius: 10px;
        }

        .results {
          margin-top: 2rem;
          width: 100%;
          border: 1px solid #eaeaea;
          border-radius: 10px;
          padding: 1rem;
        }

        .parsed-output {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .output-item {
          background-color: #f9f9f9;
          padding: 0.5rem;
          border-radius: 5px;
          font-family: Arial, sans-serif;
          color: #333;
        }

        .output-item strong {
          display: block;
          font-weight: bold;
        }

        .error {
          color: red;
          font-weight: bold;
        }
      `}</style>
    </div>
  );
}