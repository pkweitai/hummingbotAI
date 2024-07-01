import nest_asyncio
import asyncio
import argparse
import logging
import os
import threading

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

from haystack import Pipeline
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.generators.google_ai import GoogleAIGeminiChatGenerator
from haystack.components.builders import DynamicChatPromptBuilder

from hbotrc import BotListener, BotCommands

from langchain_core.runnables import RunnableSequence
from langchain_openai.chat_models import ChatOpenAI
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain_community.chat_models.ollama import ChatOllama
from typing import Dict
from hummingbot_ai.user_intent_classifier import classify_user_intent_chain, UserIntent
from google.ai.generativelanguage import Tool
from AIAgent import AiAgents  # Ensure this import is correct

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

# Global variables for bot instance and chat ID
global BOT_TOKEN, BOTID
global bot_instance, target_chat_id
global agent, main_event_loop

BOTID = "testbot"
target_chat_id = None
bot_instance = None
agent = None  # Initialize agent as None
main_event_loop = None

def cmdline_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="User intent classification test script")
    parser.add_argument("--ollama", action="store_true", help="Use Ollama instead of OpenAI")
    parser.add_argument("--google", action="store_true", help="Use Google Gemini Pro instead of OpenAI")
    return parser

# Notification handler
def on_notification(msg):
    global bot_instance, target_chat_id, main_event_loop
    _text = msg.msg
    print("[event received] " + _text + ", id " + str(target_chat_id))
    if bot_instance and target_chat_id:
        print("send message")
        asyncio.run_coroutine_threadsafe(
            send_notification(_text),
            main_event_loop
        )

async def send_notification(_text):
    global bot_instance, target_chat_id
    try:
        await bot_instance.send_message(chat_id=target_chat_id, text=f'[NOTIFICATION] - {_text}')
    except Exception as e:
        print(f"Error sending notification: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global target_chat_id
    target_chat_id = str(update.message.chat_id)  # Set the chat ID based on where /start was called
    context.user_data['active'] = True  # Set the user's active flag to True
    await update.message.reply_text('Bot started and ready to receive notifications.')

async def aichat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Aichat the user message."""
    global target_chat_id
    if context.user_data.get('active') or 1:
        try:
            response = await agent.chat_with_agent(update.message.text)
            print(response)
            await update.message.reply_text(response["msg"], parse_mode=ParseMode.MARKDOWN)
            context.user_data['active'] = True  # Set the user's active flag to True
            target_chat_id = str(update.message.chat_id)  # Set the chat ID based on where /start was called
 
        except Exception as e:
            print(f"Error in aichat: {e}")
            await update.message.reply_text("An error occurred. Please try again later.")
    else:
        await update.message.reply_text("Please use /start to activate the bot.")

async def initAgent(client):
    global agent  # Declare agent as global to modify it
    options = cmdline_parser().parse_args()
    try:
        agent = AiAgents()
        if agent is None:
            raise ValueError("Agent initialization failed!")
        await agent.setup(BOTID, options, client=client)
    except Exception as e:
        print(f"Failed to initialize agent: {e}")
        raise

def error_handler(update, context):
    print(f'Update {update} caused error {context.error}')

async def main():
    global BOT_TOKEN, bot_instance, main_event_loop

    BOT_TOKEN = os.getenv('BOT_TOKEN')
    if BOT_TOKEN is None:
        raise ValueError("BOT_TOKEN environment variable is not set")

    application = Application.builder().token(BOT_TOKEN).build()
    bot_instance = application.bot
    main_event_loop = asyncio.get_event_loop()

    # Run the application
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, aichat))
    application.add_error_handler(error_handler)

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

    client = BotCommands(
        host='localhost',
        port=1883,
        username='',
        password='',
        bot_id=BOTID,
    )

    await initAgent(client)  # Await the initialization of the agent

    # Start the listener in a new thread
    listener_thread = threading.Thread(target=start_listener, args=(listener,))
    listener_thread.start()
    print("started listener")

    application.run_polling(allowed_updates=Update.ALL_TYPES)

def start_listener(listener):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(listener.run_forever())

if __name__ == "__main__":
    # Ensure we are using a new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
