from langchain.chains import RetrievalQA # for chatting with the pdf
from langchain.llms import OpenAI # the LLM model we'll use (CHatGPT)
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.faiss import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain import OpenAI
from langchain.document_loaders import PyPDFLoader, CSVLoader
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

    SMEs = {"Claims": "John Holt", "Special Lines": "Susan Day", "Underwriting": "Sai Kanakala","MNA Mobile": "Evan Anger"}

    link  = """
        Create Html A tags by using the Technical Name as the text and the Document Location as the HREF.
        Display a list as an HTML UL tag, e.g. <ul><li>Item 1</li><li>Item 2</li></ul>
    """

    def format_smes(self, smes):
        return "\n".join([f"{key} - {value}" for key, value in smes])

    def __init__(self, store):

        self.store = store
        prompt_template = """You are the friendly DIG bot.  Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.

        {context}

        Question: gps code
        Answer: Are you looking for the GPS Code values? Or where to find the current active GPS Codes?
        Question: find the source
        Answer: I found 3 sources listed in the DIG System. Would you like to list them?
        Question: list the sources
        Answer: Here are the sources I found: <ul><li><a href=""#"">Claims Data Warehouse</a></li><li><a href=""#"">Personal Lines Data Warehouse</a></li><li><a href=""https://edm-dig-prod.prod.glb.pgrcloud.app/data-catalog"">Commercial Lines Data Warehouse</a></li></ul>
        Question: who do I contact for claims questions?
        Answer: John Holt is the SME for Claims.  He can be reached at (440) 202-1234 or <a href="enail:jholt@progressive.com">jholt@progressive.com</a>.
        
        Question: {question}
        Answer:"""
        PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question",])
        chain_type_kwargs = {"prompt": PROMPT}
        self.qa = RetrievalQA.from_chain_type(llm=OpenAI(), chain_type="stuff", retriever=self.store.as_retriever(), chain_type_kwargs=chain_type_kwargs)
    
    def query(self, question):
        return self.qa.run(question)
    
    def add_to_history(self, question, answer):
        pass

    def clear_history(self):
        self.history = []

# Provides the store for the index
class CSVStoreProvider:
    def __init__(self, filename):
        self.filename = filename
    
    def store(self):
        # openai_api_key = "OPENAI_API_KEY"
        # os.environ["OPENAI_API_KEY"] = openai_api_key

        embeddings = OpenAIEmbeddings()
        if os.path.exists("./faiss_index_csv"):
            print("loaded from index")
            vectorstore = FAISS.load_local("faiss_index_csv", embeddings)
        else:
            loader = CSVLoader(self.filename, csv_args={"delimiter": ","})
            pages = loader.load()
            print(f"Loaded from csv {self.filename}")
            # text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=50)
            # texts = text_splitter.split_documents(pages)

            vectorstore = FAISS.from_documents(pages, embeddings)
            vectorstore.save_local("faiss_index_csv")

        return vectorstore

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
            loader = PyPDFLoader(self.filename)
            pages = loader.load_and_split()
            print(f"Loaded from documents: {self.filename}")
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

    
    
