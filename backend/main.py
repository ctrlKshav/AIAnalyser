import os
import bs4
import fitz  # PyMuPDF
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
# from langchain.chains import QuestionAnsweringChain
from langchain.embeddings import HuggingFaceEmbeddings
# from langchain.llms import HuggingFaceHub
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv  # Import the dotenv function
from langchain import hub
from langchain_community.document_loaders import WebBaseLoader,TextLoader
from langchain.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_vertexai import ChatVertexAI
import vertexai

app = FastAPI()
load_dotenv(".env")

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Update with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


# Function to extract text from the uploaded PDF
def extract_text_from_pdf(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def process_text_file(text_file_path: str,question) -> str:
    

    # Load environment variables from .env file


    # Initialize Vertex AI SDK
    vertexai.init(project=os.getenv("PROJECT_ID"), location=os.getenv('REGION'))

    # Set up the language model using Vertex AI's Chat API
    llm = ChatVertexAI(model="gemini-pro")

    loader=TextLoader('./processed_files/pdf_text.txt')

   
    docs = loader.load()
    print("Dawgs")
    print(docs)

    # Split documents into chunks for processing
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    print("spips")
    # print(splits)

    # Create embeddings using Hugging Face and build the vector store with FAISS
    hf_embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(splits, hf_embeddings)

    # Set up retriever and prompt
    retriever = vectorstore.as_retriever()
    prompt = hub.pull("rlm/rag-prompt")

    # Format documents for the final output
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # Chain setup for retrieval and response generation
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    # Example query
    answer = rag_chain.invoke(question)
    print(answer)
    return answer

    # No need for delete_collection; FAISS does not have it
    # For cleanup, you may remove vectorstore's reference if needed

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
    # with open(f"./processed_files/{file.filename}.txt", "w") as f:
    with open(f"./processed_files/pdf_text.txt", "w") as f:
        f.write(text_content)
    
    return {"message": "PDF uploaded and processed successfully"}

# Define a Pydantic model for the question request
class QuestionRequest(BaseModel):
    question: str

# Endpoint to answer questions based on the extracted text
@app.post("/ask_question/")
async def ask_question(data: QuestionRequest):
    # Load the extracted text
    with open("./processed_files/pdf_text.txt", "r") as f:
        context = f.read()

    response = process_text_file("pdf_text.txt",data.question)
    
    return {"answer": response}
