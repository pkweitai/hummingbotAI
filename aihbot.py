#!/usr/bin/env python3
import asyncio
import argparse
#import dotenv
import logging
import threading
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os

from haystack import Pipeline
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.generators.google_ai import GoogleAIGeminiChatGenerator
from haystack.components.builders import DynamicChatPromptBuilder
from hbotrc import BotListener
from telegram import Update
from telegram.constants import ParseMode

from langchain_core.runnables import RunnableSequence
from langchain_openai.chat_models import ChatOpenAI
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain_community.chat_models.ollama import ChatOllama
from typing import Dict
from hummingbot_ai.user_intent_classifier import classify_user_intent_chain, UserIntent
from google.ai.generativelanguage import  Tool




# Global variables for bot instance and chat ID
global BOT_TOKEN,BOTID
global bot_instance, target_chat_id

BOTID="testbot"
target_chat_id = None
bot_instance = None


def cmdline_parser() -> argparse.ArgumentParser:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="User intent classification test script")
    parser.add_argument("--ollama", action="store_true", help="Use Ollama instead of OpenAI")
    parser.add_argument("--google", action="store_true", help="Use Google Gemini Pro instead of OpenAI")
    return parser


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
    if context.user_data.get('active'):

            #response = asyncio.run(agent.chat_with_agent(update.message.text))
            classification: UserIntent =  await gc.ainvoke({"message": update.message.text})
            response = f"User message: {update.message.text}\n User Intent: {classification}\n"
            print(response)
            await update.message.reply_text(response["msg"],parse_mode=ParseMode.MARKDOWN)
          
    else:
         await update.message.reply_text("Please use /start to activate the bot.")



def main():
    #dotenv.load_dotenv()

    BOT_TOKEN = os.getenv('BOT_TOKEN')
    BOT_TYPE = os.getenv('BOT_TYPE')
    #global agent  
    global application
    global gc
    application = Application.builder().token(BOT_TOKEN).build()
      
    cmdline_args: argparse.Namespace = cmdline_parser().parse_args()
    if cmdline_args.ollama:
        llm: ChatOllama = ChatOllama(model="llama3:70b")
    elif cmdline_args.google:
        llm: ChatGoogleGenerativeAI = ChatGoogleGenerativeAI(model="gemini-1.5-flash-001")
    else:
        llm: ChatOpenAI = ChatOpenAI(temperature=0.0)

    chain : RunnableSequence[Dict, UserIntent] = classify_user_intent_chain(llm)
    gc=chain

    # Instantiate BotListener with notification handler
    listener = BotListener(
        host='localhost',
        port=1883,
        username='',
        password='',
        bot_id=BOTID,
        notifications=True,
        events=True,
        logs=False,
        on_notification=on_notification
    )


    # Store the bot instance globally
    global bot_instance
    bot_instance = application.bot

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, aichat))


    # Run the bot and listener
    if BOT_TYPE is None:
     threading.Thread(target=asyncio.new_event_loop().run_until_complete, args=(listener.run_forever(),)).start()


    application.run_polling()


if __name__ == "__main__":
        main()
