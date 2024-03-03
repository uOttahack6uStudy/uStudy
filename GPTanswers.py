import os
from langchain.schema import HumanMessage
from langchain_openai import AzureChatOpenAI
from langchain import PromptTemplate
from langchain.chains import LLMChain
from datetime import datetime  

from PineconeRAG import SearchInPineconeIndex



# Get the API keys from environment variables
PINECONE_API_KEY = os.environ['PINECONE_API_KEY']
AZURE_OPENAI_KEY = os.environ['AZURE_OPENAI_API_KEY']



Template = """  
    You are a UChat a world-class AI assistant. Your role is to provide very precise and concise answers to queries using the sources provided. Your answers should be very consice and not long on the information available in the sources, and you should avoid making unsupported assumptions. You should strive to present using bullet points. When a direct answer is not available in the sources, you may infer the best possible response using the methodology or logic evident in the sources. Always remember to cite the page number where you found the information in APA format at the end.   
    
    Question: {question}    
    
    Please use the following sources to answer the question:    
    {DataInfo}    
      

    Todays date is: {history}
    
    Based on these sources, how would you formulate a detailed, clear, and concise response to the query? If the exact information isn't found in the sources, how would you extrapolate or infer the best possible answer using the methodology or logic inherent in the sources?  
    
    Please provide the response in a user-friendly format includes bullet points for clarity.
    """






def generate_response(message,DataInfo,GPTVersion):


    if GPTVersion :
        model = AzureChatOpenAI(
        openai_api_version="2023-05-15",
        azure_deployment="HamzaGPT4",
        )
    else:
        model = AzureChatOpenAI(
        openai_api_version="2023-05-15",
        azure_deployment="gpt-35-turbo-16k",
        )
    

    prompt = PromptTemplate(  
    input_variables=["question","history","DataInfo"],  
    template=Template  
    )  

    chain = LLMChain(llm=model, prompt=prompt)

    history = datetime.now()  
    print(history)

    

    response = chain.run(question = message,history = history,DataInfo=DataInfo)
    return response

#documentEmbeddings

    
    

