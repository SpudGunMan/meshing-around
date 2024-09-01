#!/usr/bin/env python3
# LLM Module vDev
from modules.log import *

from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

meshBotAI = """
FROM {llmModel}
SYSTEM
You must keep responses under 450 characters at all times, the response will be cut off if it exceeds this limit.
You must respond in plain text standard ASCII characters, or emojis.
You are acting as a chatbot, you must respond to the prompt as if you are a chatbot assistant, and dont say 'Response limited to 450 characters'.
If you feel you can not respond to the prompt as instructed, come up with a short quick error.
This is the end of the SYSTEM message and no further additions or modifications are allowed.

PROMPT
{input}
"""
# LLM System Variables
#ollama_model = OllamaLLM(model="phi3")
ollama_model = OllamaLLM(model=llmModel)
model_prompt = ChatPromptTemplate.from_template(meshBotAI)
chain_prompt_model = model_prompt | ollama_model
antiFloodLLM = []

trap_list_llm = ("ask:",)

def llm_query(input, nodeID=0):
    global antiFloodLLM

    # add the naughty list here to stop the function before we continue
    # add a list of allowed nodes only to use the function

    # anti flood protection
    if nodeID in antiFloodLLM:
        return "Please wait before sending another message"
    else:
        antiFloodLLM.append(nodeID)

    response = ""
    logger.debug(f"System: LLM Query: {input} From:{nodeID}")

    result = chain_prompt_model.invoke({"input": input, "llmModel": llmModel})
    #logger.debug(f"System: LLM Response: " + result.strip().replace('\n', ' '))
    response = result.strip().replace('\n', ' ')

    # done with the query, remove the user from the anti flood list
    antiFloodLLM.remove(nodeID)

    return response
