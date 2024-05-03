from io import BytesIO
from langchain_google_genai import ChatGoogleGenerativeAI
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.schema import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from pinecone import Pinecone
from langchain.prompts import PromptTemplate
import base64
import streamlit as st
from streamlit_pdf_viewer import pdf_viewer
import os



def get_conversational_chain():
    prompt_template = """
        Answer the question in detail as much as possible from the provided context, make sure to provide all the 
        details, if the answer is not in the provided context just say, "answer is not available in the context", do not
        provide the wrong answer\n\n
        Context:\n{context}?\n
        Question:\n{question}\n

        Answer:
    """
    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3, google_api_key=os.getenv("GOOGLE_API_KEY"))
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    return chain

def generate_answer(user_question, text_chunks):
    index_name = "pdf-chatbot"
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index(index_name)

    # Embed the user's question
    embeddings_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=os.getenv("GOOGLE_API_KEY"))
    query_embedding = embeddings_model.embed_query(user_question)

    # Query the Pinecone index for similar vectors
    response = index.query(
        vector=[query_embedding],
        top_k=5,
        include_values=True
    )

    # If matches are found, use conversational model to generate response
    if response.get('matches'):
        chain = get_conversational_chain()
        docs = [Document(page_content=chunk) for chunk in text_chunks]
        response_from_chain = chain(
            {"input_documents": docs, "question": user_question},
            return_only_outputs=True
        )
        print(response_from_chain["output_text"])
        return response_from_chain["output_text"]
    else:
        return "Sorry, I couldn't find relevant information to answer your question."


def extract_text_chunks(pdf_file):
    text = ""
    if isinstance(pdf_file, bytes):
        pdf_file = BytesIO(pdf_file)

    pdf_reader = PdfReader(pdf_file)
    for page in pdf_reader.pages:
        text += page.extract_text()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=10000,
        chunk_overlap=1000
    )
    return text_splitter.split_text(text)

def display_messages():
    if len(st.session_state.messages):
        for message in st.session_state.messages:
            if message['content']:
                with st.chat_message(message['role']):
                    st.markdown(message['content'])


#User Interface

st.title("Learn From PDF")
st.write("Taming the vast information locked within PDFs can be a tedious task. Here's where PDF Query tools come to the rescue. These AI-powered solutions act as your personal PDF butler, allowing you to ask natural language questions and receive precise answers directly from the document.")
st.markdown("---")

uploaded_pdf = st.file_uploader("Upload PDF", type="pdf")

if "messages" not in st.session_state:
        st.session_state.messages = []

if uploaded_pdf is not None and uploaded_pdf:
    text_chunks = [""]
    with st.spinner():
        text_chunks = extract_text_chunks(uploaded_pdf)
    user_prompt = st.chat_input("Ask Me About this Article")

    st.session_state.messages.append({
        "role": "user",
        "content": user_prompt
    })


    if user_prompt:
        with st.spinner():
            response = generate_answer(user_prompt, text_chunks)
            st.session_state.messages.append({
                "role": "ai",
                "content": response
            })
            display_messages()
    
