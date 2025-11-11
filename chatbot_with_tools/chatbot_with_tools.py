import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr
import tools

load_dotenv(override=True)

openai_api_key = os.getenv('OPENAI_API_KEY')
if openai_api_key:
    print(f"OpenAI API Key exists and begins {openai_api_key[:8]}")
else:
    print("OpenAI API Key not set")
    
MODEL = "gpt-4.1-mini"
openai = OpenAI()

# As an alternative, if you'd like to use Ollama instead of OpenAI
# Check that Ollama is running for you locally (see week1/day2 exercise) then uncomment these next 2 lines
# MODEL = "llama3.2"
# openai = OpenAI(base_url='http://localhost:11434/v1', api_key='ollama')

system_message = """
You are a helpful assistant for an Airline called FlightAI.
Give short, courteous answers, no more than 1 sentence.
Always be accurate. If you don't know the answer, say so.
"""

def chat(message, history):
    history = [{"role":h["role"], "content":h["content"]} for h in history]
    messages = [{"role": "system", "content": system_message}] + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(model=MODEL, messages=messages, tools=tools.tools)

    while response.choices[0].finish_reason=="tool_calls":
        message = response.choices[0].message
        responses = handle_tool_calls(message)
        messages.append(message)
        messages.extend(responses)
        print(f"Messages: {messages}")
        response = openai.chat.completions.create(model=MODEL, messages=messages, tools=tools.tools)
    
    return response.choices[0].message.content

def handle_tool_calls(message):
    responses = []
    for tool_call in message.tool_calls:
        func = getattr(tools, tool_call.function.name)
        print(f"Tool function: {func}")
        arguments = json.loads(tool_call.function.arguments)
        print(f"Tool function {func} arguments: {arguments}")
        func_return = func(**arguments)
        print(f"Tool function {func} with arguments {arguments} returned {func_return}")
        responses.append({
            "role": "tool",
            "content": func_return,
            "tool_call_id": tool_call.id
        })

    return responses

gr.ChatInterface(fn=chat, type="messages").launch()

