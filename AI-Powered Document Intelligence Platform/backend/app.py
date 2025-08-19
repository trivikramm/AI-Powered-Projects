from flask import Flask, request, jsonify, abort
from dotenv import load_dotenv
import os
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_pinecone import Pinecone
from langchain.chains import RetrievalQA
import google.generativeai as genai

load_dotenv()

app = Flask(__name__)

# Initialize Pinecone
pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone_environment = os.getenv("PINECONE_ENVIRONMENT")
pinecone_index_name = os.getenv("PINECONE_INDEX_NAME")

# Initialize Google Gemini
google_api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=google_api_key)
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)

docsearch = Pinecone.from_existing_index(pinecone_index_name, embeddings)

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        try:
            pdf_reader = PyPDF2.PdfReader(pdf)
            for page in pdf_reader.pages:
                text += page.extract_text()
        except PyPDF2.errors.PdfReadError:
            # Abort if a file is not a valid PDF or is corrupted
            abort(400, description=f"File '{pdf.filename}' is not a valid or uncorrupted PDF.")
    return text

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_text(text)
    return chunks

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return jsonify({"error": "No files part"}), 400
    files = request.files.getlist('files')
    if not files or all(f.filename == '' for f in files):
        return jsonify({"error": "No selected files"}), 400

    try:
        raw_text = get_pdf_text(files)
        if not raw_text.strip():
            return jsonify({"error": "Could not extract text from the provided PDF(s)."}), 400
        
        text_chunks = get_text_chunks(raw_text)
        
        Pinecone.from_texts(text_chunks, embeddings, index_name=pinecone_index_name)

        return jsonify({"message": "Files uploaded and processed successfully"})
    except Exception as e:
        # Catch exceptions from get_pdf_text and other processing steps
        return jsonify({"error": str(e)}), 500

@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.get_json()
    query = data.get('query')
    if not query:
        return jsonify({"error": "No query provided"}), 400

    qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=docsearch.as_retriever())
    response = qa.run(query)
    
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True)
