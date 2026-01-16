from ast import List
import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr
import sys
import base64
from io import BytesIO
from PIL import Image

load_dotenv(override=True)

openai_api_key = os.getenv('OPENAI_API_KEY')
if openai_api_key:
    print(f"OpenAI API Key exists and begins {openai_api_key[:8]}")
else:
    print("OpenAI API Key not set")
    
CHAT_MODEL = "gpt-4.1-mini"
GRAPHICS_MODEL = "dall-e-2"
openai = OpenAI()


class ChatbotSetup(object):

    def __init__(self):
        pass

    def get_tools(self):
        return self.tools

    def get_system_message(self):
        return self.system_message

class TravelChatbotSetup(ChatbotSetup):

    def __init__(self):
        pass

    system_message = """
        You are a helpful assistant for an Airline called FlightAI. You also have access to data about levels of danger in a country.
        Give short, courteous answers, no more than 1 sentence.
        Always be accurate. If you don't know the answer, say so.
        """

    ticket_prices = {
        "guadalajara": "$999", 
        "new orleans": "$799", 
        "prague": "$99", 
        "berlin": "$199"}

    country_danger = {
        "mexico": [5, 1], 
        "usa": [1000, 10], 
        "united states": [1000, 10],
        "estados unidos": [1000, 10],
        "czech republic": [2, 1], 
        "germany": [3, 2]}

    def get_ticket_price(self, destination_city):
        print(f"Ticket tool called for city {destination_city}")
        price = self.ticket_prices.get(destination_city.lower(), "Unknown ticket price")
        return_val = f"The price of a ticket to {destination_city} is {price}"
        print (return_val)
        return return_val

    def get_country_danger(self, country, dark_skin):
        print(f"Danger tool called for country {country} with dark skin set to {dark_skin}")
        danger = "Unknown danger level"
        if self.country_danger.get(country.lower()):
            try:
                danger = self.country_danger.get(country.lower())[0] * (self.country_danger.get(country.lower())[1] if dark_skin else 1)
            except Exception as err:
                print(f"Could not get the values for {country} and dark_skin being {dark_skin} due to {err}")
        return_val = f"The danger level in {country} is {danger}"
        print (return_val)
        return return_val

    price_function = {
        "name": "get_ticket_price",
        "description": "Get the price of a return ticket to the destination city.",
        "parameters": {
            "type": "object",
            "properties": {
                "destination_city": {
                    "type": "string",
                    "description": "The city that the customer wants to travel to",
                },
            },
            "required": ["destination_city"],
            "additionalProperties": False
        }
    }

    danger_function = {
        "name": "get_country_danger",
        "description": "Get the danger level of a country.",
        "parameters": {
            "type": "object",
            "properties": {
                "country": {
                    "type": "string",
                    "description": "The country that the customer wants to travel to",
                },
                "dark_skin": {
                    "type": "boolean",
                    "description": "Whether the customer has a dark skin tone"
                }
            },
            "required": ["country", "dark_skin"],
            "additionalProperties": False
        }
    }

    tools = [
    {"type": "function", "function": price_function},
    {"type": "function", "function": danger_function}]

class TooledChatbot:

    def __init__(self, openai, chat_model, graphics_model, chatbot_setup: ChatbotSetup):
        self.chat_model = chat_model
        self.graphics_model = graphics_model
        self.openai = openai
        self.chatbot_setup = chatbot_setup
        self.image_checkbox = None

    def handle_tool_calls(self, message):
        responses = []
        print (f"Calling {len(message.tool_calls)} tools: ")
        for tool_call in message.tool_calls:
            tool_method = getattr(self.chatbot_setup, tool_call.function.name)
            arguments = json.loads(tool_call.function.arguments)
            tool_return = tool_method(**arguments)
            responses.append({
                    "role": "tool",
                    "content": tool_return,
                    "tool_call_id": tool_call.id
                })
        return responses

    def artist(self, places:list[str]):
        image_response = openai.images.generate(
                model=self.graphics_model,
                prompt=f"An image representing a post-apocalyptic image of {', '.join(places)} having gone through a nuclear war apocalypse.",
                size="512x512",
                n=1,
                response_format="b64_json",
            )
        image_base64 = image_response.data[0].b64_json
        image_data = base64.b64decode(image_base64)
        return Image.open(BytesIO(image_data))
    
    def chat(self, history):
        history = [{"role":h["role"], "content":h["content"]} for h in history]
        # prepend system msg to history
        messages = [{"role": "system", "content": self.chatbot_setup.get_system_message()}] + history
        response = openai.chat.completions.create(model=self.chat_model, messages=messages, tools=self.chatbot_setup.get_tools())

        # sort out tool calls
        while response.choices[0].finish_reason=="tool_calls":
            message = response.choices[0].message
            responses = self.handle_tool_calls(message)
            messages.append(message)
            messages.extend(responses)
            response = openai.chat.completions.create(model=self.chat_model, messages=messages, tools=self.chatbot_setup.get_tools())
        
        # get response text
        reply = response.choices[0].message.content

        # append the response text to history
        history += [{"role":"assistant", "content":reply}]
        print (f"Full history after response: {history}")
        return history

    def add_message_to_history(self, message, history):
        history += [{"role":"user", "content":message}]
        return history


    def process_messages(self, message, history):

        print (f"Image checkbox value: {self.image_checkbox}")

        # get a list of places mentioned in the prompt
        prompt_places_list = self.extract_places_from_prompt(message)
        # if the list of places is not empty, draw a picture of them
        if len(prompt_places_list) > 0:
            image = self.artist(prompt_places_list)

        print (f"Places to generate an image: {prompt_places_list}")
        

        # send the whole history as a prompt and get history with the added LLM reply at the end
        processed_messages = self.chat(history)
        return processed_messages, image

    def extract_places_from_prompt(self, message) -> list[str]:
        system_message = "\
            You are a chatbot which is able to extract names of countries and cities from text and provide them back in the form of a JSON list.\
            Respond only in JSON list, if no countries or cities have been found in the text, respond with an empty JSON list\
            Example text: I would like to fly to new orleans in the united states.\
            Example response: [\"New Orleans\", \"United States of America\"]"
        response = openai.chat.completions.create(
            model=self.chat_model, 
            messages=[{"role": "system", "content": system_message}, {"role": "user", "content": message}]
            )
        resp_content = response.choices[0].message.content
        try:
            return json.loads(resp_content)
        except Exception as ex:
            print(f"Exception {ex} ocurred while trying to decode response {resp_content}")
            return []

    def run_chatbot(self):


        with gr.Blocks() as ui:
            with gr.Row():
                with gr.Column():
                    chatbot = gr.Chatbot(height=500)
                with gr.Column():
                    with gr.Row():
                        self.image_checkbox = gr.Checkbox(label = "Generate image")
                    with gr.Row():
                        image_output = gr.Image(height=500, interactive=False)
            with gr.Row():
                message = gr.Textbox(label="Chat with our AI Assistant:")

        # Hooking up events to callbacks

            message.submit(
                self.add_message_to_history, 
                inputs=[message, chatbot], 
                outputs=[chatbot]).then(
                    self.process_messages, 
                    inputs=[message, chatbot], 
                    #outputs=[chatbot] # no img generation for now
                    outputs=[chatbot, image_output]
            )

        ui.launch(inbrowser=True, auth=("b", "b"))

        #gr.ChatInterface(fn=self.chat, type="messages").launch()


TooledChatbot(openai, CHAT_MODEL, GRAPHICS_MODEL, TravelChatbotSetup()).run_chatbot()