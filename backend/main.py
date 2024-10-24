from fastapi import FastAPI, File, UploadFile
import os

app = FastAPI()

UPLOAD_FOLDER = "uploaded_pdfs"

@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    file_location = f"{UPLOAD_FOLDER}/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
    return {"info": "file uploaded successfully", "filename": file.filename}
