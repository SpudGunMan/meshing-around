#!/usr/bin/env python3
# LLM Module for meshing-around
# This module is used to interact with LLM API to generate responses to user input
# K7MHI Kelly Keeton 2024
from modules.log import *

# Ollama Client
# https://github.com/ollama/ollama/blob/main/docs/faq.md#how-do-i-configure-ollama-server
import requests
import json

if not rawLLMQuery:
    # this may be removed in the future
    from googlesearch import search # pip install googlesearch-python

# Tooling Functions Defined Here
# Example: current_time function
def llmTool_current_time():
    """
    Example tool function to get the current time.
    :return: Current time string.
    """
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')

llmFunctions = [

    {
        "name": "llmTool_current_time",
        "description": "Get the current time.",
        "parameters": {
            "type": "object",
            "properties": {}
    }
    }
]

# LLM System Variables
ollamaAPI = ollamaHostName + "/api/generate"
tokens = 450 # max charcters for the LLM response, this is the max length of the response also in prompts
requestTruncation = True # if True, the LLM "will" truncate the response 

openaiAPI = "https://api.openai.com/v1/completions" # not used, if you do push a enhancement!

# Used in the meshBotAI template
llmEnableHistory = True # enable last message history for the LLM model
llmContext_fromGoogle = True # enable context from google search results adds to compute time but really helps with responses accuracy

googleSearchResults = 3 # number of google search results to include in the context more results = more compute time
antiFloodLLM = []
llmChat_history = {}
trap_list_llm = ("ask:", "askai")

meshbotAIinit = """
    keep responses as short as possible. chatbot assistant no followuyp questions, no asking for clarification.
    You must respond in plain text standard ASCII characters or emojis.
    """

truncatePrompt = f"truncate this as short as possible:\n"

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

def get_google_context(input, num_results):
    # Get context from Google search results
    googleResults = []
    try:
        googleSearch = search(input, advanced=True, num_results=num_results)
        if googleSearch:
            for result in googleSearch:
                googleResults.append(f"{result.title} {result.description}")
        else:
            googleResults = ['no other context provided']
    except Exception as e:
        logger.debug(f"System: LLM Query: context gathering failed, likely due to network issues")
        googleResults = ['no other context provided']
    return googleResults

def send_ollama_query(llmQuery):
    # Send the query to the Ollama API and return the response
    result = requests.post(ollamaAPI, data=json.dumps(llmQuery))
    if result.status_code == 200:
        result_json = result.json()
        result = result_json.get("response", "")
        # deepseek has added <think> </think> tags to the response
        if "<think>" in result:
            result = result.split("</think>")[1]
    else:
        raise Exception(f"HTTP Error: {result.status_code}")
    return result

def send_ollama_tooling_query(prompt, functions, model=None, max_tokens=450):
    """
    Send a prompt and function/tool definitions to Ollama API for function calling.
    :param prompt: The user prompt string.
    :param functions: List of function/tool definitions (see Ollama API docs).
    :param model: Model name (optional, defaults to llmModel).
    :param max_tokens: Max tokens for response.
    :return: Ollama API response JSON.
    """
    if model is None:
        model = llmModel
    payload = {
        "model": model,
        "prompt": prompt,
        "functions": functions,
        "stream": False,
        "max_tokens": max_tokens
    }
    result = requests.post(ollamaAPI, data=json.dumps(payload))
    if result.status_code == 200:
        return result.json()
    else:
        raise Exception(f"HTTP Error: {result.status_code} - {result.text}")

def llm_query(input, nodeID=0, location_name=None):
    global antiFloodLLM, llmChat_history
    googleResults = []

    # if this is the first initialization of the LLM the query of " " should bring meshbotAIinit OTA shouldnt reach this?
    # This is for LLM like gemma and others now?
    if input == " " and rawLLMQuery:
        logger.warning("System: These LLM models lack a traditional system prompt, they can be verbose and not very helpful be advised.")
        input = meshbotAIinit
    else:
        input = input.strip()
        # classic model for gemma2, deepseek-r1, etc
        logger.debug(f"System: Using classic LLM model framework, ideally for gemma2, deepseek-r1, etc")

    if not location_name:
        location_name = "no location provided "
    
    # remove askai: and ask: from the input
    for trap in trap_list_llm:
        if input.lower().startswith(trap):
            input = input[len(trap):].strip()
            break

    # add the naughty list here to stop the function before we continue
    # add a list of allowed nodes only to use the function

    # anti flood protection
    if nodeID in antiFloodLLM:
        return "Please wait before sending another message"
    else:
        antiFloodLLM.append(nodeID)

    if llmContext_fromGoogle and not rawLLMQuery:
        googleResults = get_google_context(input, googleSearchResults)

    history = llmChat_history.get(nodeID, ["", ""])

    if googleResults:
        logger.debug(f"System: Google-Enhanced LLM Query: {input} From:{nodeID}")
    else:
        logger.debug(f"System: LLM Query: {input} From:{nodeID}")
    
    response = ""
    result = ""
    location_name += f" at the current time of {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}"

    try:
        if rawLLMQuery:
            # sanitize the input to remove tool call syntax
            if '```' in input:
                logger.warning("System: LLM Query: Code markdown detected, removing for raw query")
            input = input.replace('```bash', '').replace('```python', '').replace('```', '')
            modelPrompt = input
        else:
            # Build the query from the template
            modelPrompt = meshBotAI.format(input=input, context='\n'.join(googleResults), location_name=location_name, llmModel=llmModel, history=history)
            
        llmQuery = {"model": llmModel, "prompt": modelPrompt, "stream": False, "max_tokens": tokens}
        # Query the model via Ollama web API
        result = send_ollama_query(llmQuery)

        #logger.debug(f"System: LLM Response: " + result.strip().replace('\n', ' '))
    except Exception as e:
        antiFloodLLM.remove(nodeID)  # Ensure removal on error
        logger.warning(f"System: LLM failure: {e}")
        return "⛔️I am having trouble processing your request, please try again later."
    
    # cleanup for message output
    response = result.strip().replace('\n', ' ')
    
    if rawLLMQuery and requestTruncation and len(response) > 450:
        #retryy loop to truncate the response
        logger.warning(f"System: LLM Query: Response exceeded {tokens} characters, requesting truncation")
        truncateQuery = {"model": llmModel, "prompt": truncatePrompt + response, "stream": False, "max_tokens": tokens}
        truncateResult = send_ollama_query(truncateQuery)

        # cleanup for message output
        response = result.strip().replace('\n', ' ')

    # done with the query, remove the user from the anti flood list
    antiFloodLLM.remove(nodeID)

    if llmEnableHistory:
        llmChat_history[nodeID] = [input, response]

    return response
