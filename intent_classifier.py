#!/usr/bin/env python

import argparse
import asyncio
#from dotenv import load_dotenv
from langchain_core.runnables import RunnableSequence
from langchain_openai.chat_models import ChatOpenAI
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain_community.chat_models.ollama import ChatOllama
from typing import Dict

from hummingbot_ai.user_intent_classifier import classify_user_intent_chain, UserIntent


TEST_USER_MESSAGES = [
    "gmgm",
    "Anything new from memecoins today?",
    "Notify me when ETH drops by 3% or more",
    "Give me my NAV chart",
    "What do you think about the new Ryzen 9000 CPUs from AMD?",
    "What are news notification settings?",
    "Buy me 20000 MEME right now",
    "Should I give my cat some treat?",
    "Sell 0.1 BTC with limit price $69000",
    "What's the biggest crypto news today?",
    "Hi Hummingbot!",
    "Should I buy Bitcoin today?",
    "Why did Bitcoin prices drop today?",
]


def cmdline_parser() -> argparse.ArgumentParser:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="User intent classification test script")
    parser.add_argument("--ollama", action="store_true", help="Use Ollama instead of OpenAI")
    parser.add_argument("--google", action="store_true", help="Use Google Gemini Pro instead of OpenAI")
    return parser


async def main():
    #load_dotenv()

    cmdline_args: argparse.Namespace = cmdline_parser().parse_args()
    if cmdline_args.ollama:
        llm: ChatOllama = ChatOllama(model="llama3:70b")
    elif cmdline_args.google:
        llm: ChatGoogleGenerativeAI = ChatGoogleGenerativeAI(model="gemini-1.5-flash-001")
    else:
        llm: ChatOpenAI = ChatOpenAI(temperature=0.0)

    chain: RunnableSequence[Dict, UserIntent] = classify_user_intent_chain(llm)

    for user_message in TEST_USER_MESSAGES:
        classification: UserIntent = await chain.ainvoke({"message": user_message})
        print(f"User message: {user_message}\n{classification}\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
