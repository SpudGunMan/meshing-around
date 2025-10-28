#!/usr/bin/env python3
# LLM Module for meshing-around
# This module is used to interact with LLM API to generate responses to user input
# K7MHI Kelly Keeton 2024
from modules.log import logger
from modules.settings import (llmModel, ollamaHostName, rawLLMQuery, 
                              llmUseWikiContext, useOpenWebUI, openWebUIURL, openWebUIAPIKey, cmdBang, urlTimeoutSeconds)

# Ollama Client
# https://github.com/ollama/ollama/blob/main/docs/faq.md#how-do-i-configure-ollama-server
import requests
import json
from datetime import datetime

# LLM System Variables
ollamaAPI = ollamaHostName + "/api/generate"
openWebUIChatAPI = openWebUIURL + "/api/chat/completions"
openWebUIOllamaProxy = openWebUIURL + "/ollama/api/generate"
tokens = 450 # max charcters for the LLM response, this is the max length of the response also in prompts
requestTruncation = True # if True, the LLM "will" truncate the response 

# Used in the meshBotAI template
llmEnableHistory = True # enable last message history for the LLM model

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

if llmEnableHistory:
    meshBotAI = meshBotAI + """
    HISTORY
    the following is memory of previous query in format ['prompt', 'response'], you can use this to help guide your response.
    {history}

    """

# Tooling Functions Defined Here
# Example: current_time function
def llmTool_current_time():
    """
    Example tool function to get the current time.
    :return: Current time string.
    """
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')

def llmTool_math_calculator(expression):
    """
    Example tool function to perform basic math calculations.
    :param expression: A string containing a math expression (e.g., "2 + 2").
    :return: The result of the calculation as a string.
    """
    try:
        # WARNING: Using eval can be dangerous if not controlled properly.
        # This is a simple example; in production, consider using a safe math parser.
        result = eval(expression, {"__builtins__": None}, {})
        return str(result)
    except Exception as e:
        return f"Error in calculation: {e}"

llmFunctions = [

    {
        "name": "llmTool_current_time",
        "description": "Get the current time.",
        "parameters": {
            "type": "object",
            "properties": {}
    }
    },
    {
        "name": "llmTool_math_calculator",
        "description": "Perform basic math calculations.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "A math expression to evaluate, e.g., '2 + 2'."
                }
            },
            "required": ["expression"]
        }
    },
]

def get_wiki_context(input):
    """
    Get context from Wikipedia/Kiwix for RAG enhancement
    :param input: The user query
    :return: Wikipedia summary or empty string if not available
    """
    try:
        from modules.wiki import get_wikipedia_summary
        # Extract potential search terms from the input
        # Try to identify key topics/entities for Wikipedia search
        search_terms = extract_search_terms(input)
        
        wiki_context = []
        for term in search_terms[:2]:  # Limit to 2 searches to avoid excessive API calls
            summary = get_wikipedia_summary(term)
            if summary and "error" not in summary.lower():
                wiki_context.append(f"Wikipedia context for '{term}': {summary}")
        
        return '\n'.join(wiki_context) if wiki_context else ''
    except Exception as e:
        logger.debug(f"System: LLM Query: Wiki context gathering failed: {e}")
        return ''

def extract_search_terms(input):
    """
    Extract potential search terms from user input
    Simple implementation: look for capitalized words, proper nouns, etc.
    :param input: The user query
    :return: List of potential search terms
    """
    # Remove common command prefixes
    for trap in trap_list_llm:
        if input.lower().startswith(trap):
            input = input[len(trap):].strip()
            break
    
    # Simple heuristic: extract capitalized words and phrases
    words = input.split()
    search_terms = []
    
    # Look for multi-word capitalized phrases
    temp_phrase = []
    for word in words:
        # Remove punctuation for checking
        clean_word = word.strip('.,!?;:')
        if clean_word and clean_word[0].isupper() and len(clean_word) > 2:
            temp_phrase.append(clean_word)
        elif temp_phrase:
            search_terms.append(' '.join(temp_phrase))
            temp_phrase = []
    
    if temp_phrase:
        search_terms.append(' '.join(temp_phrase))
    
    # If no capitalized terms found, use the whole query
    if not search_terms:
        search_terms = [input.strip()]
    
    return search_terms[:3]  # Limit to 3 terms

def send_openwebui_query(prompt, model=None, max_tokens=450, context=''):
    """
    Send query to OpenWebUI API for chat completion
    :param prompt: The user prompt
    :param model: Model name (optional, defaults to llmModel)
    :param max_tokens: Max tokens for response
    :param context: Additional context to include
    :return: Response text or error message
    """
    if model is None:
        model = llmModel
    
    headers = {
        'Authorization': f'Bearer {openWebUIAPIKey}',
        'Content-Type': 'application/json'
    }
    
    messages = []
    if context:
        messages.append({
            "role": "system",
            "content": f"Use the following context to help answer questions:\n{context}"
        })
    
    messages.append({
        "role": "user",
        "content": prompt
    })
    
    data = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "stream": False
    }
    
    try:
        result = requests.post(openWebUIChatAPI, headers=headers, json=data, timeout=10)
        if result.status_code == 200:
            result_json = result.json()
            # OpenWebUI returns OpenAI-compatible format
            if 'choices' in result_json and len(result_json['choices']) > 0:
                response = result_json['choices'][0]['message']['content']
                return response.strip()
            else:
                logger.warning(f"System: OpenWebUI API returned unexpected format")
                return "⛔️ Response Error"
        else:
            logger.warning(f"System: OpenWebUI API returned status code {result.status_code}")
            return f"⛔️ Request Error"
    except requests.exceptions.RequestException as e:
        logger.warning(f"System: OpenWebUI API request failed: {e}")
        return f"⛔️ Request Error"

def send_ollama_query(llmQuery):
    # Send the query to the Ollama API and return the response
    try:
        result = requests.post(ollamaAPI, data=json.dumps(llmQuery), timeout= urlTimeoutSeconds * 4)
        if result.status_code == 200:
            result_json = result.json()
            result = result_json.get("response", "")
            # deepseek has added <think> </think> tags to the response
            if "<think>" in result:
                result = result.split("</think>")[1]
        else:
            logger.warning(f"System: LLM Query: Ollama API returned status code {result.status_code}")
            return f"⛔️ Request Error"
        return result
    except requests.exceptions.RequestException as e:
        logger.warning(f"System: LLM Query: Ollama API request failed: {e}")
        return f"⛔️ Request Error"

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

def llm_query(input, nodeID=0, location_name=None, init=False):
    global antiFloodLLM, llmChat_history
    wikiContext = ''

    # if this is the first initialization of the LLM the query of " " should bring meshbotAIinit OTA shouldnt reach this?
    # This is for LLM like gemma and others now?
    if init and rawLLMQuery:
        logger.warning("System: These LLM models lack a traditional system prompt, they can be verbose and not very helpful be advised.")
        input = meshbotAIinit
    elif init:
        input = input.strip()
        # classic model for gemma2, deepseek-r1, etc
        logger.debug(f"System: Using SYSTEM model framework, ideally for gemma2, deepseek-r1, etc")


    # Remove command bang if present
    if cmdBang:
        input = input[1:].strip()

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

    # Get Wikipedia/Kiwix context if enabled (RAG)
    if llmUseWikiContext and input != meshbotAIinit:
        # get_wiki_context returns a string, but we want to count the items before joining
        search_terms = extract_search_terms(input)
        wiki_context_list = []
        for term in search_terms[:2]:
            summary = get_wiki_context(term)
            if summary and "error" not in summary.lower():
                wiki_context_list.append(f"Wikipedia context for '{term}': {summary}")
        wikiContext = '\n'.join(wiki_context_list) if wiki_context_list else ''
        if wikiContext:
            logger.debug(f"System: using Wikipedia/Kiwix context for LLM query got {len(wiki_context_list)} results")

    history = llmChat_history.get(nodeID, ["", ""])

    logger.debug(f"System: LLM Query: {input} From:{nodeID}")
    
    response = ""
    result = ""
    location_name += f" at the current time of {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}"

    try:
        # Use OpenWebUI if enabled
        if useOpenWebUI and openWebUIAPIKey:
            logger.debug("System: Using OpenWebUI API")
            
            # Combine all context sources
            combined_context = []
            if wikiContext:
                combined_context.append(wikiContext)
            
            context_str = '\n\n'.join(combined_context)
            
            # For OpenWebUI, we send a cleaner prompt
            if rawLLMQuery:
                result = send_openwebui_query(input, context=context_str, max_tokens=tokens)
            else:
                # Use the template for non-raw queries
                modelPrompt = meshBotAI.format(
                    input=input, 
                    context=context_str if combined_context else 'no other context provided',
                    location_name=location_name, 
                    llmModel=llmModel, 
                    history=history
                )
                result = send_openwebui_query(modelPrompt, max_tokens=tokens)
        else:
            # Use standard Ollama API
            if rawLLMQuery:
                # sanitize the input to remove tool call syntax
                if '```' in input:
                    logger.warning("System: LLM Query: Code markdown detected, removing for raw query")
                input = input.replace('```bash', '').replace('```python', '').replace('```', '')
                modelPrompt = input
                
                # Add wiki context to raw queries if available
                if wikiContext:
                    modelPrompt = f"Context:\n{wikiContext}\n\nQuestion: {input}"
            else:
                # Build the query from the template
                all_context = []
                if wikiContext:
                    all_context.append(wikiContext)
                
                context_text = '\n'.join(all_context) if all_context else 'no other context provided'
                modelPrompt = meshBotAI.format(
                    input=input, 
                    context=context_text,
                    location_name=location_name, 
                    llmModel=llmModel, 
                    history=history
                )
                
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
        response = truncateResult.strip().replace('\n', ' ')

    # done with the query, remove the user from the anti flood list
    antiFloodLLM.remove(nodeID)

    if llmEnableHistory:
        llmChat_history[nodeID] = [input, response]

    return response
