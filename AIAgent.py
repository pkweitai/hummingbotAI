import logging
import threading


from featuretable import HummingBotTools
from hummingbot_ai.user_intent_classifier import classify_user_intent_chain, UserIntent
from hummingbot_ai.user_generalchat import response_user_generalchat

from langchain_core.runnables import RunnableSequence
from typing import Dict
from langchain_core.runnables import RunnableSequence
from langchain_openai.chat_models import ChatOpenAI
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain_community.chat_models.ollama import ChatOllama


class AiAgents:
       
    async def setup(self, BOTID=None, cmdline_args=None) -> None:
        if cmdline_args.ollama:
            llm = ChatOllama(model="llama3:70b")
        elif cmdline_args.google:
            llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-001")
        else:
            llm = ChatOpenAI(temperature=0.0)

        self.llm = llm
        self.chain: RunnableSequence[Dict, UserIntent] = classify_user_intent_chain(llm)
        self.chatchain : RunnableSequence[Dict, str] = response_user_generalchat(llm) 

    async def chat_with_agent(self, user_input):
        classification: UserIntent = await self.chain.ainvoke({"message": user_input})
        results = f" Your Intent seems to be : {classification}\n"
        print(results)
        
        botAnswers: str = await self.chatchain.ainvoke({"message": user_input})
        print(botAnswers)
        
        results+="\n"
        results+=botAnswers
        
        return {"msg": results, "status": 1}