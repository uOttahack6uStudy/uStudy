import os
from langchain_community.document_loaders import UnstructuredPDFLoader      
from pinecone import Pinecone
from langchain.embeddings import AzureOpenAIEmbeddings
from pinecone import Pinecone, PodSpec

# Get the API keys from environment variables
PINECONE_API_KEY = os.environ['PINECONE_API_KEY']
AZURE_OPENAI_KEY = os.environ['AZURE_OPENAI_API_KEY']

 
def SearchInPineconeIndex(APIKey,OpenAIKey,IndexName,Query,User,k=3):
            
    embeddings =  AzureOpenAIEmbeddings(openai_api_key = OpenAIKey)  # Generating embeddings


    pc = Pinecone(api_key = APIKey )
    index = pc.Index(IndexName )

    Vector = embeddings.embed_documents([Query])

    #Result = index.query(
    #vector=Vector[0],
    #top_k=k,
    #include_values=True,
    #include_metadata=True,
    #filter={"user": {"$eq": "Test2"}}
    #)
    #print(Result)
    Result = index.query( namespace=User,vector=Vector[0],top_k=k, include_values=True,include_metadata=True)
    
    TextRes  = [Text['metadata']['text'] + f" [Found in page {Text['metadata']['page']}] " for Text in Result['matches']]
    #print(TextRes)
    return TextRes




