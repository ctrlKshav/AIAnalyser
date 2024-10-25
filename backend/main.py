from fastapi import FastAPI, File, UploadFile
import os
import fitz 




app = FastAPI()

UPLOAD_FOLDER = "../uploaded_pdfs"


@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    file_location = f"{UPLOAD_FOLDER}/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())

    doc = fitz.open(file_location)
    text = ""
    for page in doc:
        text += page.get_text()

    return {"info": "file uploaded successfully", "filename": file.filename, "content": text}



@app.post("/ask_question/")
async def ask_question(document_id: str, question: str):
    # Load document text from database or file
    text = load_text_from_document(document_id)
    
    # Create an index (this can be optimized and stored in memory)
    index = GPTSimpleVectorIndex.from_text(text)
    
    # Process the question
    answer = index.query(question)
    return {"answer": str(answer)}