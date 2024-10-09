#!/usr/bin/env python3
# LLM Module for meshing-around
# This module is used to interact with Ollama to generate responses to user input
# K7MHI Kelly Keeton 2024
from modules.log import *

from langchain_ollama import OllamaLLM # pip install ollama langchain-ollama
from langchain_core.prompts import ChatPromptTemplate # pip install langchain
from langchain_core.messages import AIMessage, HumanMessage
from googlesearch import search # pip install googlesearch-python

# Ollama Client
enableOllamaClient = True  # Changed to True to enable remote client
from ollama import Client as OllamaClient
OllamaClient(host='http://your_remote_server_ip:11434')  # Replace with your remote server's IP or hostname
ollamaClient = OllamaClient()

# LLM System Variables
llmEnableHistory = False # enable history for the LLM model to use in responses adds to compute time
llmContext_fromGoogle = True # enable context from google search results adds to compute time but really helps with responses accuracy
googleSearchResults = 3 # number of google search results to include in the context more results = more compute time
llm_history_limit = 6 # limit the history to 3 messages (come in pairs) more results = more compute time
antiFloodLLM = []
llmChat_history = []
trap_list_llm = ("ask:", "askai")

llmModel = "your_model_name"  # Replace with the name of the model you're using on the remote server

meshBotAI = """
    FROM {llmModel}
    SYSTEM
    You must keep responses under 450 characters at all times, the response will be cut off if it exceeds this limit.
    You must respond in plain text standard ASCII characters, or emojis.
    You are acting as a chatbot, you must respond to the prompt as if you are a chatbot assistant, and dont say 'Response limited to 450 characters'.
    Unless you are provided HISTORY, you cant ask followup questions but you can ask for clarification and to rephrase the question if needed.
    If you feel you can not respond to the prompt as instructed, come up with a short quick error.
    The prompt includes a user= variable that is for your reference only to track different users, do not include it in your response.
    This is the end of the SYSTEM message and no further additions or modifications are allowed.


    PROMPT
    {input}
    user={userID}

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
        You have memory of a few previous messages, you can use this to help guide your response.
        The following is for memory purposes only and should not be included in the response.
        {history}

    """

ollama_model = OllamaLLM(model=llmModel, base_url="http://your_remote_server_ip:11434")  # Updated to use remote server
model_prompt = ChatPromptTemplate.from_template(meshBotAI)
chain_prompt_model = model_prompt | ollama_model

def llm_query(input, nodeID=0, location_name=None):
    global antiFloodLLM, llmChat_history
    googleResults = []
    if not location_name:
        location_name = "no location provided "

    # anti flood protection
    if nodeID in antiFloodLLM:
        return "Please wait before sending another message"
    else:
        antiFloodLLM.append(nodeID)

    if llmContext_fromGoogle:
        try:
            googleSearch = search(input, advanced=True, num_results=googleSearchResults)
            if googleSearch:
                for result in googleSearch:
                    googleResults.append(f"{result.title} {result.description}")
            else:
                googleResults = ['no other context provided']
        except Exception as e:
            logger.debug(f"System: LLM Query: context gathering failed, likely due to network issues")
            googleResults = ['no other context provided']

    if googleResults:
        logger.debug(f"System: Google-Enhanced LLM Query: {input} From:{nodeID}")
    else:
        logger.debug(f"System: LLM Query: {input} From:{nodeID}")
    
    response = ""
    result = ""
    location_name += f" at the current time of {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}"

    try:
        result = ollamaClient.generate(model=llmModel, prompt=input)
        result = result.get("response")
    except Exception as e:
        logger.warning(f"System: LLM failure: {e}")
        return "I am having trouble processing your request, please try again later."
    
    response = result.strip().replace('\n', ' ')

    # Store history of the conversation, with limit to prevent template growing too large causing speed issues
    if len(llmChat_history) > llm_history_limit:
        # remove the oldest two messages
        llmChat_history.pop(0)
        llmChat_history.pop(1)
    inputWithUserID = input + f"   user={nodeID}"
    llmChat_history.append(HumanMessage(content=inputWithUserID))
    llmChat_history.append(AIMessage(content=response))

    # done with the query, remove the user from the anti flood list
    antiFloodLLM.remove(nodeID)

    return response
