import React, { useState } from 'react';

const PDFUpload: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [uploadMessage, setUploadMessage] = useState<string | null>(null);
  const [question, setQuestion] = useState<string>('');
  const [answer, setAnswer] = useState<string | null>(null);

  // Handle file selection
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
    }
  };

  // Handle PDF upload
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      alert("Please select a file first");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch('http://localhost:8000/upload_pdf/', {
        method: 'POST',
        body: formData,
      });
      const result = await response.json();
      setUploadMessage(result.message); // Adjusted to match backend response
    } catch (error) {
      console.error("Error uploading the file:", error);
    }
  };

  // Handle question submission
  const handleQuestionSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
  
    if (!question) {
      alert("Please enter a question.");
      return;
    }
  
    try {
      const response = await fetch('http://localhost:8000/ask_question/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question }), // Sends as JSON
      });
  
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
  
      const result = await response.json();
      setAnswer(result.answer);
    } catch (error) {
      console.error("Error asking the question:", error);
    }
  };
    
  
  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input type="file" onChange={handleFileChange} accept="application/pdf" />
        <button type="submit">Upload PDF</button>
      </form>
      {uploadMessage && <p>{uploadMessage}</p>}

      <form onSubmit={handleQuestionSubmit}>
        <input 
          type="text" 
          value={question} 
          onChange={(e) => setQuestion(e.target.value)} 
          placeholder="Ask a question" 
        />
        <button type="submit">Ask Question</button>
      </form>
      {answer && <p>Answer: {answer}</p>}
    </div>
  );
};

export default PDFUpload;
