#!/usr/bin/env python3
import asyncio
import sys
import logging
import threading
import requests
import subprocess  # Import subprocess to run system commands
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes


#  AI imports
import os
from operator import itemgetter
from typing import Dict, List, Union

import re
import json
from haystack import Pipeline, component
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from haystack_integrations.components.generators.google_ai import GoogleAIGeminiGenerator
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.generators.google_ai import GoogleAIGeminiChatGenerator
from haystack.components.builders import DynamicChatPromptBuilder
from hbotrc import BotListener, BotCommands


from google.ai.generativelanguage import FunctionDeclaration, Tool
from featuretable_devops import  DevOpTools


# Global variables for bot instance and chat ID
global BOT_TOKEN,BOTID
global bot_instance, target_chat_id

BOT_TOKEN = '6825139485:AAELY1WCcqwpCUsgUFbof_abOcEplayh6bA'  # Your TG bot token
BOTID="testbot"
target_chat_id = None
bot_instance = None

def dumpcontents(res): 
     contents=[]
     for item in res:
          contents.append(item.content)
     return contents


def pipebuilder():
    global pipeline ,pipeline2
    global llm

    #Tool dispatch
    prompt_builder = DynamicChatPromptBuilder()

    tool = Tool(function_declarations=htable.getFTable())
    llm =GoogleAIGeminiChatGenerator(
                model="gemini-pro",
                tools=[tool]
    )

    # Create and configure the pipeline
    pipeline = Pipeline()
    pipeline.add_component("prompt_builder", prompt_builder)
    pipeline.add_component("llm", llm)
    pipeline.connect("prompt_builder.prompt", "llm.messages")

# Main app function
def chat_with_agent(user_input):
    # Run the pipeline to determine the action and tool response
    messages = [ChatMessage.from_user(content=user_input)]
    res = pipeline.run(data=
                       {"prompt_builder": {
                            "template_variables":{"location": "Mexico",
                                                  "command" : "start" ,
                                                  "desc" : " " 
                                                  },
                            "prompt_source": messages}})

    print(res)

    tool_messages = htable.dispatch(res["llm"]["replies"])
    if(tool_messages and tool_messages[0].name is None):
         message = tool_messages[0].content 
         return { "msg" :message, "status" : 0}
    else:
        # complete message from tool responses
        messages += res["llm"]["replies"] + tool_messages
        print(messages)
        print("\n\n")
        print(tool_messages)
        res = llm.run(messages=messages)
        contents= dumpcontents(res["replies"])
        return { "msg" : contents[0], "status" : 1}
    

def websearch(msg):
    # Create and configure the pipeline
    prompt_builder2 = DynamicChatPromptBuilder()
    llm_chat=GoogleAIGeminiChatGenerator(model="gemini-pro" )

    pipe = Pipeline()
    pipe.add_component("prompt_builder2", prompt_builder2)
    pipe.add_component("llm_chat", llm_chat)
    pipe.connect("prompt_builder2.prompt", "llm_chat.messages")

    system_message = ChatMessage.from_system("You are a helpful customer service agent giving out short summary of ansewrs you found")
    messages = [ChatMessage.from_user("{{aimsg}} Summarize in one sentence")]

    searchcontent = pipe.run(data={"prompt_builder2": {"template_variables": {"aimsg": msg}, "prompt_source": messages}})

    print(searchcontent)
    return searchcontent["llm_chat"]["replies"][0].content



# Notification handler
def on_notification(msg):
    global bot_instance, target_chat_id
    _text = msg.msg
    print("[event] "+_text +", id" + target_chat_id )
    if bot_instance and target_chat_id:
        asyncio.run(bot_instance.send_message(chat_id=target_chat_id, text=f'[NOTIFICATION] - {_text}'))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global target_chat_id
    target_chat_id = str(update.message.chat_id)  # Set the chat ID based on where /start was called
    context.user_data['active'] = True  # Set the user's active flag to True
    await update.message.reply_text('Bot started and ready to receive notifications.')

async def aichat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Aichat the user message."""
    if context.user_data.get('active') or True:

            response = chat_with_agent(update.message.text)
            print(response)
            if(response["status"] == 1)  or response["msg"] !={} :
                await update.message.reply_text(response["msg"])
            else:
                await update.message.reply_text(" ...")
                await update.message.reply_text(websearch(update.message.text))

    else:
         await update.message.reply_text("Please use /start to activate the bot.")




def main():
    
    global application
    application = Application.builder().token(BOT_TOKEN).build()

    
    global htable
    htable = DevOpTools(username="rex", 
                        token="11674e095f68011018a1ed0a413e999f39", 
                        base_url="https://fa7b-98-35-34-89.ngrok-free.app")


    # build pipelines
    pipebuilder()
    # Store client in bot data
    #application.bot_data['client'] = client


    # Store the bot instance globally
    global bot_instance
    bot_instance = application.bot

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, aichat))

    # Run the bot and listener
    #threading.Thread(target=asyncio.new_event_loop().run_until_complete, args=(listener.run_forever(),)).start()
    application.run_polling()


if __name__ == "__main__":
    main()
