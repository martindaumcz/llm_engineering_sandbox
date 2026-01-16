import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr
import tools
from config import config

load_dotenv(override=True)

openai_api_key = os.getenv('OPENAI_API_KEY')
if openai_api_key:
    print(f"OpenAI API Key exists and begins {openai_api_key[:8]}")
else:
    print("OpenAI API Key not set")
    
openai = OpenAI()

def chat(message, history):
    history = [{"role":h["role"], "content":h["content"]} for h in history]
    messages = [{"role": "system", "content": system_message}] + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(model=model_dropdown, messages=messages, tools=tools.tools)

    while response.choices[0].finish_reason=="tool_calls":
        message = response.choices[0].message
        responses = handle_tool_calls(message)
        messages.append(message)
        messages.extend(responses)
        print(f"Messages: {messages}")
        response = openai.chat.completions.create(model=model_dropdown, messages=messages, tools=tools.tools)
    
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

available_models = config.get_all_models()

model_dropdown = gr.Dropdown(
    choices=available_models,
    value=available_models[0] if available_models else None,
    label="Model",
    info="Select the LLM model to use"
)

system_message = gr.Textbox(
    label="System Message",
    value=config.default_system_message,
    lines=4,
    info="Configure the AI's behavior and personality"
)
gr.ChatInterface(fn=chat, type="messages", additional_inputs=[model_dropdown, system_message]).launch()

