from langchain.chains import RetrievalQA # for chatting with the pdf
from langchain.llms import OpenAI # the LLM model we'll use (CHatGPT)
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.faiss import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain import OpenAI
from langchain.document_loaders import PyPDFLoader
from langchain.prompts import PromptTemplate
import os

# This class provides a history of the conversation
class ConversationalQueryProvider:
    def __init__(self, store):
        self.store = store
        self.history = []
        prompt_template = """You are Flo, the friendly Progressive Insurance bot.  Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.

        {context}

        Question: {question}
        Answer in a congenial tone:"""
        PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
        chain_type_kwargs = {"prompt": PROMPT}
        self.qa = RetrievalQA.from_chain_type(llm=OpenAI(), chain_type="stuff", retriever=self.store.as_retriever(), chain_type_kwargs=chain_type_kwargs)
    
    def query(self, question):
        local_history = self.get_history()
        print(local_history + question)
        return self.qa.run(local_history + question)
    
    def add_to_history(self, question, answer):
        self.history.append({"question": question, "answer": answer})

    def get_history(self):
        return "The previous conversation was: \n".join([f"Human: {qa['question']}\nFlo: {qa['answer']}" for qa in self.history]) + "\n"
    
    def clear_history(self):
        self.history = []

# This class does not have a history of the conversation
class RetrievalQAQueryProvider:
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
    
    def add_to_history(self, question, answer):
        pass

# Provides the store for the index
class PDFStoreProvider:
    def __init__(self, filename):
        self.filename = filename
    
    def store(self):
        # openai_api_key = "OPENAI_API_KEY"
        # os.environ["OPENAI_API_KEY"] = openai_api_key

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

# Actual bot that answers questions
class AnswerBot():

    def __init__(self, query):
        self.query = query
 
    def get_answer(self, question):
        answer = self.query.query(question)
        self.query.add_to_history(question, answer)
        return answer

    
    
