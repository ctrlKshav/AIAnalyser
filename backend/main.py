import os
from dotenv import load_dotenv  # Loading dotenv to access environment variables

# PyMuPDF
import fitz  

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from langchain import hub
from langchain_community.document_loaders import TextLoader,WebBaseLoader
from langchain.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_vertexai import ChatVertexAI
import vertexai

app = FastAPI()
load_dotenv(".env")

# Setting up CORS to enable cross-origin requests from frontend
app.add_middleware(
    CORSMiddleware,
    # allow_origins=[os.getenv('LOCALHOST')],  # My Frontend URL
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)


# Function to extract text from the uploaded PDF file
def extract_text_from_pdf(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Function to handle text processing for querying
def process_text_file(text_file_path: str, question) -> str:
    
    # Initialize Vertex AI using project settings from the .env file
    vertexai.init(project=os.getenv("PROJECT_ID"), location=os.getenv('REGION'))

    # Configuring Vertex AI model for response generation
    llm = ChatVertexAI(model="gemini-pro")

    # Load the extracted text as a document
    loader = TextLoader('./processed_files/pdf_text.txt')

    #Testing the website search and it works pretty easy
    # loader = WebBaseLoader('https://realkeshav.vercel.app')

    # Loading the document data and confirm it loads correctly
    docs = loader.load()
    print("Documents loaded:", docs)

    # Split documents into manageable chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    print("Document split completed")

    # Create embeddings and initialize vector storage with FAISS
    hf_embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(splits, hf_embeddings) 

    # Configure retriever and prompt for querying
    retriever = vectorstore.as_retriever()
    prompt = hub.pull("rlm/rag-prompt")

    # Format documents to include in the final output
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # Setting up a chain for query retrieval and response generation
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    # Generate the answer by invoking the chain with the question
    answer = rag_chain.invoke(question)
    print(answer)
    return answer

# Endpoint to upload PDF and extract text
@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    pdf_path = f"../uploaded_pdfs/{file.filename}"
    
    # Ensuring directory exists to save uploaded PDFs
    os.makedirs("../uploaded_pdfs", exist_ok=True)
    
    # Saving the uploaded PDF to the specified path
    with open(pdf_path, "wb") as f:
        f.write(await file.read())
    
    # Extract text content from the PDF
    text_content = extract_text_from_pdf(pdf_path)
    
    # Save extracted text for later processing
    with open(f"./processed_files/pdf_text.txt", "w") as f:
        f.write(text_content)
    
    return {"message": "PDF uploaded and processed successfully"}
    
# Define a Pydantic model for the question request format
class QuestionRequest(BaseModel):
    question: str

# Endpoint to answer questions based on extracted text
@app.post("/ask_question/")
async def ask_question(data: QuestionRequest):
    # Load the saved text content to use as context for the question
    with open("./processed_files/pdf_text.txt", "r") as f:
        context = f.read()

    # Pass context and question to processing function and get response
    response = process_text_file("pdf_text.txt", data.question)
    
    return {"answer": response}
