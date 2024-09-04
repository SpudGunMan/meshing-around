#!/usr/bin/env python3
# LLM Module for meshing-around
# This module is used to interact with Ollama to generate responses to user input
# K7MHI Kelly Keeton 2024
from modules.log import *

from langchain_ollama import OllamaLLM # pip install ollama langchain-ollama
from langchain_core.prompts import ChatPromptTemplate # pip install langchain
from langchain_core.messages import AIMessage, HumanMessage
from googlesearch import search # pip install googlesearch-python

# LLM System Variables
llmEnableHistory = False
llmContext_fromGoogle = True
googleSearchResults = 3
llm_history_limit = 6 # limit the history to 3 messages (come in pairs)
antiFloodLLM = []
llmChat_history = []
trap_list_llm = ("ask:", "askai")

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
    The following is the location the user
    {location_name}

    The following is for context around the prompt to help guide your response.
    {context}

    """
else:
    meshBotAI = meshBotAI + """
    CONTEXT
    The following is the location the user
    {location_name}

    """

if llmEnableHistory:
    meshBotAI = meshBotAI + """
    HISTORY
    You have memory of a few previous messages, you can use this to help guide your response.
    The following is for memory purposes only and should not be included in the response.
    {history}

    """

#ollama_model = OllamaLLM(model="phi3")
ollama_model = OllamaLLM(model=llmModel)
model_prompt = ChatPromptTemplate.from_template(meshBotAI)
chain_prompt_model = model_prompt | ollama_model

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
        try:
            googleSearch = search(input, advanced=True, num_results=googleSearchResults)
            if googleSearch:
                for result in googleSearch:
                    # SearchResult object has url= title= description= just grab title and description
                    googleResults.append(f"{result.title} {result.description}")
            else:
                googleResults = ['no other context provided']
        except Exception as e:
            logger.debug(f"System: LLM Query: context gathering error: {e}")
            googleResults = ['no other context provided']


    if googleResults:
        logger.debug(f"System: External LLM Query: {input} From:{nodeID} with context from google")
    else:
        logger.debug(f"System: External LLM Query: {input} From:{nodeID}")
    
    response = ""
    result = ""
    location_name += f" at the current time of {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    result = chain_prompt_model.invoke({"input": input, "llmModel": llmModel, "userID": nodeID, \
                                        "history": llmChat_history, "context": googleResults, "location_name": location_name})
    #logger.debug(f"System: LLM Response: " + result.strip().replace('\n', ' '))

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
