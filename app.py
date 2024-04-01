# -*- coding=utf-8 -*-
import streamlit as st
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from llm_chatglm import ChatGLM
from langchain.embeddings import HuggingFaceEmbeddings

# Customize the layout
st.set_page_config(page_title="DOCAI", page_icon="xxx", layout="wide", )

# function for writing uploaded file in temp
def write_text_file(content, file_path):
    try:
        with open(file_path, 'w') as file:
            file.write(content)
        return True
    except Exception as e:
        print(f"Error occurred while writing the file: {e}")
        return False

# set prompt template
prompt_template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.

{context}

Question: {question}
Answer:"""
prompt = PromptTemplate(template=prompt_template,
                        input_variables=["context", "question"])

llm = ChatGLM()

model_name = "./models"
model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': False}

embeddings_model = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)

llm_chain = LLMChain(llm=llm, prompt=prompt)

st.title("Document Conversation ")
uploaded_file = st.file_uploader("Upload an article", type="txt")

if uploaded_file is not None:
    content = uploaded_file.read().decode('utf-8')
    file_path = "temp/file.txt"
    write_text_file(content, file_path)

    loader = TextLoader(file_path)
    docs = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=0)
    texts = text_splitter.split_documents(docs)
    db = Chroma.from_documents(texts, embeddings_model)
    st.success("File Loaded Successfully!!")

    # Query through LLM    
    question = st.text_input("Ask something from the file",
                             placeholder="Find something similar to: ....this.... in the text?",
                             disabled=not uploaded_file, )
    if question:
        similar_doc = db.similarity_search(question, k=1)
        print("similar_doc")
        print(similar_doc)
        print("\n")
        context = similar_doc[0].page_content
        print(context)
        print("\n")
        query_llm = LLMChain(llm=llm, prompt=prompt)
        response = query_llm.run({"context": context, "question": question})
        st.write(response)
