from langchain.chains import ChatVectorDBChain, RetrievalQA # for chatting with the pdf
from langchain.llms import OpenAI # the LLM model we'll use (CHatGPT)
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.faiss import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain import OpenAI
from langchain.document_loaders import PyPDFLoader
from langchain.prompts import PromptTemplate

import os

class QueryProvider:
    def __init__(self, store):
        self.store = store
        prompt_template = """You are Flo, the friendly Progressive Insurance bot.  Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.

        {context}

        Question: {question}
        Answer in a congenial tone:"""
        PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
        chain_type_kwargs = {"prompt": PROMPT}
        self.qa = RetrievalQA.from_chain_type(llm=OpenAI(), chain_type="stuff", retriever=self.store.as_retriever(), chain_type_kwargs=chain_type_kwargs)
    
    def query(self, question):
        return self.qa.run(question)

class StoreProvider:
    def __init__(self, filename):
        self.filename = filename
    
    def store(self):
        openai_api_key = "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"
        os.environ["OPENAI_API_KEY"] = openai_api_key

        embeddings = OpenAIEmbeddings()
        if os.path.exists("./faiss_index"):
            print("loaded from index")
            vectorstore = FAISS.load_local("faiss_index", embeddings)
        else:
            pdf_path = "./AnswersList.pdf"
            loader = PyPDFLoader(pdf_path)
            pages = loader.load_and_split()
            print("Loaded from documents")
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=50)
            texts = text_splitter.split_documents(pages)
            vectorstore = FAISS.from_documents(texts, embeddings)
            vectorstore.save_local("faiss_index")

        return vectorstore

class PGROracle():

    def __init__(self, query):
        self.query = query
 
    def get_answer(self, question):
        return "Flo says: " + self.query.query(question)
    
