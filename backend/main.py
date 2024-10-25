import os
import fitz  # PyMuPDF
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from transformers import pipeline
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()



# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Update with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Load the Hugging Face question-answering pipeline
qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")

# Function to extract text from the uploaded PDF
def extract_text_from_pdf(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Endpoint to upload PDF and extract text
@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    pdf_path = f"../uploaded_pdfs/{file.filename}"
    
    # Ensure the directory exists
    os.makedirs("../uploaded_pdfs", exist_ok=True)
    
    # Save the uploaded PDF
    with open(pdf_path, "wb") as f:
        f.write(await file.read())
    
    # Extract text from the PDF
    text_content = extract_text_from_pdf(pdf_path)
    
    # Save extracted text for later use
    with open("pdf_text.txt", "w") as f:
        f.write(text_content)
    
    return {"message": "PDF uploaded and processed successfully"}

# Define a Pydantic model for the question request
class QuestionRequest(BaseModel):
    question: str

# Endpoint to answer questions based on the extracted text
@app.post("/ask_question/")
async def ask_question(data: QuestionRequest):
    # Load the extracted text
    with open("pdf_text.txt", "r") as f:
        context = f.read()
    
    # Use the Hugging Face model to answer the question
    response = qa_pipeline(question=data.question, context=context)
    print(response)
    
    return {"answer": response["answer"]}
