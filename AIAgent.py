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
from typing import List, Callable, Dict


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


    async def dispatch(self,intent: UserIntent, params: List[str],user_input):
        status="\n"
        if intent in self.function_table:
            status+=self.function_table[intent](params)
        else:
            print(f"No handler found" )

        res=f"make a human friendly message for 'based on user input :{user_input}, the detected intent: {intent} , and hummingbot result:  {status}, repeat all parameters precisely, no need ask question to confirm \n'"

        humanreadables : str = await self.chatchain.ainvoke({"message": res})
        
        return humanreadables

    def handle_greeting(params: List[str] = None) -> str:
        if params is None or not params:
            return "Completed Greeting: Success"
        return f"Completed Greeting: Success, Parameters: {params}"

    def handle_general_status(params: List[str] = None) -> str:
        if params is None or not params:
            return "Completed General Status: Success"
        return f"Completed General Status: Success, Parameters: {params}"

    def handle_market_information(params: List[str] = None) -> str:
        if params is None or not params:
            return "Completed Market Information: Success"
        return f"Completed Market Information: Success, Parameters: {params}"

    def handle_portfolio_information(params: List[str] = None) -> str:
        if params is None or not params:
            return "Completed Portfolio Information: Success"
        results = " please make a dummy account statement list for me with ETH, BTC , exhcange name, date "
        return f"Completed Portfolio Information: Success, Parameters: {params} ," + results

    def handle_price_alerts(params: List[str] = None) -> str:
        if params is None or not params:
            return "Completed Price Alerts: Success"
        return f"Completed Price Alerts: Success, Parameters: {params}"

    def handle_news_alerts(params: List[str] = None) -> str:
        if params is None or not params:
            return "Completed News Alerts: Success"
        return f"Completed News Alerts: Success, Parameters: {params}"

    def handle_trading(params: List[str] = None) -> str:
        if params is None or not params:
            return "Completed Trading: Success"
        return f"Completed Trading: Success, Parameters: {params}"

    def handle_chat(params: List[str] = None) -> str:
        if params is None or not params:
            return "Completed Chat: Success"
        return f"Completed Chat: Success, Parameters: {params}"


    async def chat_with_agent(self, user_input):
        classification: UserIntent
        parameters: List[str]
        aianswers : str
    
        classification, parameters ,aianswers = await self.chain.ainvoke({"message": user_input})
        results = f"  Intent : {classification}\n"
        results += f" param :  {parameters}\n"
        print(results)
        
        #botAnswers: str = await self.chatchain.ainvoke({"message": user_input})
        botAnswers: str = await self.dispatch(classification,parameters,user_input)
        botAnswers +=aianswers
        print(botAnswers)
        
        return {"msg": botAnswers, "status": 1}
    

    function_table: Dict[UserIntent, Callable[[List[str]], None]] = {
        UserIntent.Greeting: handle_greeting,
        UserIntent.GeneralStatus: handle_general_status,
        UserIntent.MarketInformation: handle_market_information,
        UserIntent.PortfolioInformation: handle_portfolio_information,
        UserIntent.PriceAlerts: handle_price_alerts,
        UserIntent.NewsAlerts: handle_news_alerts,
        UserIntent.Trading: handle_trading,
        UserIntent.Chat: handle_chat,
    }