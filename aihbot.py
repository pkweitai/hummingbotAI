#!/usr/bin/env python3
import asyncio
import logging
import threading
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes


from haystack import Pipeline
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.generators.google_ai import GoogleAIGeminiChatGenerator
from haystack.components.builders import DynamicChatPromptBuilder
from hbotrc import BotListener


from google.ai.generativelanguage import  Tool
from featuretable import HummingBotTools
from AIAgent import AiAgents



# Global variables for bot instance and chat ID
global BOT_TOKEN,BOTID
global bot_instance, target_chat_id

BOT_TOKEN = '6777854610:AAG6O6Qjt6Ohf5_PZvc0s-G8HGaJOPahPpg'  # Default Bot token, please replace with ur own botToken
BOTID="testbot"
target_chat_id = None
bot_instance = None


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

            response = agent.chat_with_agent(update.message.text)
            print(response)
            await update.message.reply_text(response["msg"])
          
    else:
         await update.message.reply_text("Please use /start to activate the bot.")



def main():
    global application
    application = Application.builder().token(BOT_TOKEN).build()
      
    global agent  
    agent=AiAgents(BOTID)


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
    threading.Thread(target=asyncio.new_event_loop().run_until_complete, args=(listener.run_forever(),)).start()


    application.run_polling()


if __name__ == "__main__":
    main()
