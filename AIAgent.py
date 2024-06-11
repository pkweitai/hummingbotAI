import logging
import threading
import os

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
import requests


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
            status+=self.function_table[intent](self,params)
        else:
            print(f"No handler found" )

        res=f"make a human friendly message for 'based on user input :{user_input}, the detected intent: {intent} , and hummingbot result:  {status}, repeat all parameters precisely, no need ask question to confirm \n'"

        humanreadables : str = await self.chatchain.ainvoke({"message": res})
        
        return humanreadables

    def fetch_latest_crypto_news(self,api_key: str) -> str:
        url = f'https://newsapi.org/v2/top-headlines?country=us&category=business&apiKey={api_key}'
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an HTTPError if the HTTP request returned an unsuccessful status code
            news_data = response.json()
            
            if news_data['status'] == 'ok':
                articles = news_data['articles']
                news_list = [{"title": article['title'], "url": article['url']} for article in articles]
                
                # Format the output as a markdown string
                markdown_output = ""
                for item in news_list:
                    markdown_output += f"### [{item['title']}]({item['url']})\n\n"
                
                return markdown_output
            else:
                return f"Failed to fetch news: {news_data['status']}"
        except requests.exceptions.RequestException as e:
            return f"An error occurred: {e}"


    def handle_greeting(self,params: List[str] = None) -> str:
        if params is None or not params:
            return "Completed Greeting: Success"
        return f"Completed Greeting: Success, Parameters: {params}"

    def handle_general_status(self,params: List[str] = None) -> str:
        if params is None or not params:
            return "Completed General Status: Success"
        return f"Completed General Status: Success, Parameters: {params} " 

    def handle_market_information(self,params: List[str] = None) -> str:
        apikey = os.getenv('NEWS_API_KEY')  # Get the API key from the environment variable
        return f"Completed Market Information: Success, Parameters: {params}" + self.fetch_latest_crypto_news(apikey)


    def handle_portfolio_information(self,params: List[str] = None) -> str:
        if params is None or not params:
            return "Completed Portfolio Information: Success"
        results = " please make a dummy account statement list for me with ETH, BTC , exhcange name, date "
        return f"Completed Portfolio Information: Success, Parameters: {params} ," + results

    def handle_price_alerts(self,params: List[str] = None) -> str:
        if params is None or not params:
            return "Completed Price Alerts: Success"
        return f"Completed Price Alerts: Success, Parameters: {params}"

    def handle_news_alerts(self,params: List[str] = None) -> str:
        if params is None or not params:
            return "Completed News Alerts: Success"
        return f"Completed News Alerts: Success, Parameters: {params}"

    def handle_trading(self,params: List[str] = None) -> str:
        if params is None or not params:
            return "Completed Trading: Success"
        return f"Completed Trading: Success, Parameters: {params}"

    def handle_chat(self,params: List[str] = None) -> str:
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