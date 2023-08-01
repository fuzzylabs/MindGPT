from langchain import PromptTemplate, HuggingFacePipeline
from langchain.chains import RetrievalQA
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.schema import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.document_loaders.csv_loader import CSVLoader
from transformers import pipeline

# Load document file
with open("nhs-context.txt") as f:
    nhs_texts = f.read().split("\n\n")

# load the document and split it into chunks
documents = [Document(page_content=text) for text in nhs_texts]

print("Documents loaded:", len(documents))

# # split it into chunks
# text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
# documents = text_splitter.split_documents(documents)

# create the open-source embedding function
embedding_function = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-base")

# load it into Chroma
vectorstore = Chroma.from_documents(documents, embedding_function)

print("Documents found:", len(vectorstore.search("what is depression?", "similarity")))

template_from_notebook = """Use the following pieces of context to answer the question at the end.
If you don't know the answer, just say that you don't know, don't try to make up an answer.
Use three sentences maximum and keep the answer as concise as possible.
Always say "thanks for asking!" at the end of the answer.
{context}
Question: {question}
Helpful Answer:"""

template_from_app = "Question: {question}\n\nContext: {context}\n\n"

QA_CHAIN_PROMPT_NOTEBOOK = PromptTemplate(input_variables=["context", "question"], template=template_from_notebook)
QA_CHAIN_PROMPT_APP = PromptTemplate(input_variables=["context", "question"], template=template_from_app)

max_length = 128 #@param {type:"integer"}
temperature = 0 #@param {type:"integer"}
load_8_bit = False #@param {type:"boolean"}

llm = pipeline(
    model="google/flan-t5-base",
    task="text2text-generation",
    model_kwargs={"max_length": max_length, "load_in_8bit": load_8_bit, "temperature": temperature},
)

questions = ["What is depression?"]

hf_llm = HuggingFacePipeline(pipeline=llm)
qa_chain_notebook = RetrievalQA.from_chain_type(
    llm=hf_llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
    chain_type_kwargs={"prompt": QA_CHAIN_PROMPT_NOTEBOOK}
)
qa_chain_app = RetrievalQA.from_chain_type(
    llm=hf_llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
    chain_type_kwargs={"prompt": QA_CHAIN_PROMPT_APP}
)

for question in questions:
    result_notebook = qa_chain_notebook({"query": question})
    result_app = qa_chain_app({"query": question})
    print("="*80)
    print("Question:\t", question)
    print("="*80)
    print("Answer (notebook):\t", result_notebook["result"])
    print("="*80)
    print("Answer (app):\t", result_app["result"])
    print("="*80)
