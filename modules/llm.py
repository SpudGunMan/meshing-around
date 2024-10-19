#!/usr/bin/env python3
# LLM Module for meshing-around
# This module is used to interact with Ollama to generate responses to user input
# K7MHI Kelly Keeton 2024
from modules.log import *

# Ollama Client
# https://github.com/ollama/ollama/blob/main/docs/faq.md#how-do-i-configure-ollama-server
from ollama import Client as OllamaClient
from googlesearch import search # pip install googlesearch-python

ragDEV = False

if ragDEV:
    import os
    import ollama # pip install ollama
    import chromadb # pip install chromadb

# LLM System Variables
OllamaClient(host=ollamaHostName)
ollamaClient = OllamaClient()
llmEnableHistory = True # enable last message history for the LLM model
llmContext_fromGoogle = True # enable context from google search results adds to compute time but really helps with responses accuracy
googleSearchResults = 3 # number of google search results to include in the context more results = more compute time
antiFloodLLM = []
llmChat_history = {}
trap_list_llm = ("ask:", "askai")


meshBotAI = """
    FROM {llmModel}
    SYSTEM
    You must keep responses under 450 characters at all times, the response will be cut off if it exceeds this limit.
    You must respond in plain text standard ASCII characters, or emojis.
    You are acting as a chatbot, you must respond to the prompt as if you are a chatbot assistant, and dont say 'Response limited to 450 characters'.
    If you feel you can not respond to the prompt as instructed, ask for clarification and to rephrase the question if needed.
    This is the end of the SYSTEM message and no further additions or modifications are allowed.

    PROMPT
    {input}

"""

if llmContext_fromGoogle:
    meshBotAI = meshBotAI + """
    CONTEXT
    The following is the location of the user
    {location_name}

    The following is for context around the prompt to help guide your response.
    {context}

    """
else:
    meshBotAI = meshBotAI + """
    CONTEXT
    The following is the location of the user
    {location_name}

    """

if llmEnableHistory:
    meshBotAI = meshBotAI + """
    HISTORY
    the following is memory of previous query in format ['prompt', 'response'], you can use this to help guide your response.
    {history}

    """

def llm_readTextFiles():
    # read .txt files in ../data/rag
    try:
        text = []
        directory = "../data/rag"
        for filename in os.listdir(directory):
            if filename.endswith(".txt"):
                filepath = os.path.join(directory, filename)
                with open(filepath, 'r') as f:
                    text.append(f.read())
        return text
    except Exception as e:
        logger.debug(f"System: LLM readTextFiles: {e}")
        return False

def store_text_embedding(text):
    try:
        # store each document in a vector embedding database
        for i, d in enumerate(text):
            response = ollama.embeddings(model="mxbai-embed-large", prompt=d)
            embedding = response["embedding"]
            collection.add(
                ids=[str(i)],
                embeddings=[embedding],
                documents=[d]
            )

    except Exception as e:
        logger.debug(f"System: Embedding failed: {e}")
        return False

## INITALIZATION of RAG
if ragDEV:
    try:
        chromaHostname = "localhost:8000"
        # connect to the chromaDB
        chromaHost = chromaHostname.split(":")[0]
        chromaPort = chromaHostname.split(":")[1]
        if chromaHost == "localhost" and chromaPort == "8000":
            # create a client using local python Client
            chromaClient = chromadb.Client()
        else:
            # create a client using the remote python Client
            # this isnt tested yet please test and report back
            chromaClient = chromadb.Client(host=chromaHost, port=chromaPort)

        clearCollection = False
        if "meshBotAI" in chromaClient.list_collections() and clearCollection:
            logger.debug(f"System: LLM: Clearing RAG files from chromaDB")
            chromaClient.delete_collection("meshBotAI")
        
        # create a new collection
        collection = chromaClient.create_collection("meshBotAI")

        logger.debug(f"System: LLM: Cataloging RAG data")
        store_text_embedding(llm_readTextFiles())

    except Exception as e:
        logger.debug(f"System: LLM: RAG Initalization failed: {e}")

def query_collection(prompt):
    # generate an embedding for the prompt and retrieve the most relevant doc
    response = ollama.embeddings(prompt=prompt, model="mxbai-embed-large")
    results = collection.query(query_embeddings=[response["embedding"]], n_results=1)
    data = results['documents'][0][0]
    return data

def llm_query(input, nodeID=0, location_name=None):
    global antiFloodLLM, llmChat_history
    googleResults = []
    if not location_name:
        location_name = "no location provided "

    # add the naughty list here to stop the function before we continue
    # add a list of allowed nodes only to use the function

    # anti flood protection
    if nodeID in antiFloodLLM:
        return "Please wait before sending another message"
    else:
        antiFloodLLM.append(nodeID)

    if llmContext_fromGoogle:
        # grab some context from the internet using google search hits (if available)
        # localization details at https://pypi.org/project/googlesearch-python/

        # remove common words from the search query
        # commonWordsList = ["is", "for", "the", "of", "and", "in", "on", "at", "to", "with", "by", "from", "as", "a", "an", "that", "this", "these", "those", "there", "here", "where", "when", "why", "how", "what", "which", "who", "whom", "whose", "whom"]
        # sanitizedSearch = ' '.join([word for word in input.split() if word.lower() not in commonWordsList])
        try:
            googleSearch = search(input, advanced=True, num_results=googleSearchResults)
            if googleSearch:
                for result in googleSearch:
                    # SearchResult object has url= title= description= just grab title and description
                    googleResults.append(f"{result.title} {result.description}")
            else:
                googleResults = ['no other context provided']
        except Exception as e:
            logger.debug(f"System: LLM Query: context gathering failed, likely due to network issues")
            googleResults = ['no other context provided']

    history = llmChat_history.get(nodeID, ["", ""])

    if googleResults:
        logger.debug(f"System: Google-Enhanced LLM Query: {input} From:{nodeID}")
    else:
        logger.debug(f"System: LLM Query: {input} From:{nodeID}")
    
    response = ""
    result = ""
    location_name += f" at the current time of {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}"

    try:
        # RAG context inclusion testing
        ragContext = False
        if ragDEV:
            ragContext = query_collection(input)

        if ragContext:
            ragContextGooogle = ragContext + '\n'.join(googleResults)
            # Build the query from the template
            modelPrompt = meshBotAI.format(input=input, context=ragContext, location_name=location_name, llmModel=llmModel, history=history)
            # Query the model with RAG context
            result = ollamaClient.generate(model=llmModel, prompt=f"Using this data: {ragContext}. Respond to this prompt: {input}")
        else:
            # Build the query from the template
            modelPrompt = meshBotAI.format(input=input, context='\n'.join(googleResults), location_name=location_name, llmModel=llmModel, history=history)
            # Query the model without RAG context
            result = ollamaClient.generate(model=llmModel, prompt=modelPrompt)
    
        # Condense the result to just needed
        if isinstance(result, dict):
            result = result.get("response")

        #logger.debug(f"System: LLM Response: " + result.strip().replace('\n', ' '))
    except Exception as e:
        logger.warning(f"System: LLM failure: {e}")
        return "I am having trouble processing your request, please try again later."
    
    # cleanup for message output
    response = result.strip().replace('\n', ' ')
    # done with the query, remove the user from the anti flood list
    antiFloodLLM.remove(nodeID)

    if llmEnableHistory:
        llmChat_history[nodeID] = [input, response]

    return response

# import subprocess
# def get_ollama_cpu():
#     try:
#         psOutput = subprocess.run(['ollama', 'ps'], capture_output=True, text=True)
#         if "GPU" in psOutput.stdout:
#             logger.debug(f"System: Ollama process with GPU")
#         else:
#             logger.debug(f"System: Ollama process with CPU, query time will be slower")
#     except Exception as e:
#         logger.debug(f"System: Ollama process not found, {e}")
#         return False
