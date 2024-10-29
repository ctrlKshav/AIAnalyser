import { useState, useEffect, useRef } from 'react';
import { Button } from "./components/button";
import { Input } from "./components/input";
import { Upload, Send } from 'lucide-react';

const PDFUpload = () => {
  const [file, setFile] = useState<File | null>(null);
  const [question, setQuestion] = useState<string>('');
  const [qaHistory, setQaHistory] = useState<{ question: string; answer: string | null }[]>([]);
  const [uploadMessage, setUploadMessage] = useState<string | null>(null);
  const chatEndRef = useRef<HTMLDivElement | null>(null); // Ref for auto-scrolling

  // Handle file selection
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
    }
  };

  // Handle PDF upload
  const handleUpload = async () => {
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
      setUploadMessage("PDF Uploaded and processed successfully");

      // Clear the message after 3 seconds
      setTimeout(() => setUploadMessage(null), 3000);
    } catch (error) {
      console.error("Error uploading the file:", error);
    }
  };

  // Handle question submission
  const handleQuestionSubmit = async () => {
    if (!question) {
      alert("Please enter a question.");
      return;
    }

    // Immediately add the question to history with a null answer
    const questionEntry = { question, answer: null };
    setQaHistory((prevHistory) => [...prevHistory, questionEntry]);

    try {
      const response = await fetch('http://localhost:8000/ask_question/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question }),
      });
      const result = await response.json();

      // Update the last entry with the answer
      setQaHistory((prevHistory) => {
        const updatedHistory = [...prevHistory];
        updatedHistory[updatedHistory.length - 1] = {
          question,
          answer: result.answer,
        };
        return updatedHistory;
      });

      // Clear the input field after submission
      setQuestion('');
    } catch (error) {
      console.error("Error asking the question:", error);
    }
  };

  // Handle Enter key press
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault(); // Prevent form submission if inside a form
      handleQuestionSubmit();
      setQuestion('');

    }
  };

  // Scroll to the bottom whenever qaHistory updates
  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [qaHistory]);

  return (
    <div className="flex flex-col h-screen bg-white">
      <header className="flex items-center justify-between p-4 border-b">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
            <span className="text-white font-bold">ai</span>
          </div>
          <span className="font-semibold text-lg hidden md:inline">planet</span>
        </div>
        <div className="flex items-center space-x-4">
          {file ? (
            <span
              onClick={() => document.getElementById('file-input')?.click()}
              className="cursor-pointer text-blue-600 underline"
            >
              {file.name}
            </span>
          ) : (
            <Button
              variant="outline"
              size="sm"
              className="flex items-center space-x-2"
              onClick={() => document.getElementById('file-input')?.click()}
            >
              <Upload className="w-4 h-4" />
              <span className="hidden md:inline">Select PDF</span>
            </Button>
          )}
          <input
            id="file-input"
            type="file"
            onChange={handleFileChange}
            accept="application/pdf"
            className="hidden"
          />
          {/* Upload Button */}
          <Button
            variant="outline"
            size="sm"
            className="flex items-center space-x-2"
            onClick={handleUpload}
            disabled={!file}
          >
            <Upload className="w-4 h-4" />
            <span>Upload PDF</span>
          </Button>
        </div>
      </header>

      <main className="flex-grow overflow-auto p-4 space-y-4">
        {uploadMessage && <p className="text-green-600">{uploadMessage}</p>}

        {/* Display the question and answer history */}
        {qaHistory.map((qa, index) => (
          <div key={index} className="space-y-2">
            <div className="flex items-start space-x-2">
              <div className="w-8 h-8 bg-purple-200 rounded-full flex items-center justify-center text-purple-700">
                Q
              </div>
              <div className="bg-gray-100 rounded-lg p-2 max-w-[80%]">
                {qa.question}
              </div>
            </div>
            {qa.answer && (
              <div className="flex items-start space-x-2 justify-end">
                <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center text-white">
                  ai
                </div>
                <div className="bg-green-100 rounded-lg p-2 max-w-[80%]">
                  {qa.answer}
                </div>
              </div>
            )}
          </div>
        ))}
        {/* Ref for auto-scrolling */}
        <div ref={chatEndRef} />
      </main>

      <footer className="p-4 border-t">
        <div className="flex items-center space-x-2">
          <Input
            type="text"
            placeholder="Ask a question..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleKeyDown} // Add the key down handler
            className="flex-grow"
          />
          <Button size="icon" onClick={handleQuestionSubmit}>
            <Send className="w-4 h-4" />
            <span className="sr-only">Send message</span>
          </Button>
        </div>
      </footer>
    </div>
  );
};

export default PDFUpload;
