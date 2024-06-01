from haystack.dataclasses import ChatMessage
from google.ai.generativelanguage import FunctionDeclaration
from hbotrc import BotCommands
from newsapi import NewsApiClient

# function Table

class HummingBotTools:
       
    def __init__(self,BOTID,llm) -> None:
              self.llm=llm
              self.client= BotCommands(
                            host='localhost',
                            port=1883,
                            username='',
                            password='',
                            bot_id=BOTID  # This should be dynamic or configurable
                        )
                # Initialize the News API client
              self.newsapi = NewsApiClient(api_key=os.getenv('NEWS_API_KEY'))


    def websearch(self, user_msg: str):
      response={user_msg : ""}
      messages = [ChatMessage.from_user(content=user_msg)]
      searchcontent = self.llm.run( messages = messages)
      response["user_msg"] = searchcontent["replies"][0].content
      return response

    websearch_func = FunctionDeclaration(
        name="websearch",
        description="Performs a simulated web search using a large language model and returns the main content of the first reply.",
        parameters={
            "type_": "OBJECT",
            "properties": {
                "user_msg": {"type_": "STRING", "description": "The user's message or query to search for"},
            },
            "required": ["user_msg"],
        },
    )


    def search_news(self, topic: str):
            # Fetch top headlines using specific parameters
            articles = self.newsapi.get_top_headlines(
                q='crypto',
                sources='bbc-news,the-verge',
                category='business',
                language='en',
                country='us'
            )
            # Collect titles and URLs from the articles
            news_list = [{"title": article["title"], "url": article["url"]} for article in articles["articles"]]
            return news_list

    search_news_func = FunctionDeclaration(
        name="search_news",
        description="Search top news headlines based on a topic and return headlines and URLs",
        parameters={
            "type_": "OBJECT",
            "properties": {
                "topic": {"type_": "STRING", "description": "The topic to search for in news articles"},
            },
            "required": ["topic"],
        },
    )



    def get_current_weather(self,location: str, unit: str = "celsius"):  # noqa: ARG001
            return {"weather": "sunny", "temperature": 21.8, "unit": unit}

    get_current_weather_func = FunctionDeclaration(
            name="get_current_weather",
            description="Get the current weather in a given location",
            parameters={
                "type_": "OBJECT",
                "properties": {
                    "location": {"type_": "STRING", "description": "The city and state, e.g. San Francisco, CA"},
                    "unit": {
                        "type_": "STRING",
                        "enum": [
                            "celsius",
                            "fahrenheit",
                        ],
                    },
                },
                "required": ["location"],
            },
        )



    # Function to invoke another function based on 'res' structure
    def dispatch(self,results):
        # Extract the necessary details from 'res'
        responses=[]

        for reply in results:
            function_name = reply.name
            parameters = reply.content

            # Check if the function exists in the global scope
            if function_name is not None:
                func = getattr(self, function_name, None)
                # Call the function with the unpacked parameters
                if callable(func):
                    result = func(**parameters)
                    responses.append(ChatMessage.from_function(content=result, name=function_name))
            else:
                responses.append(ChatMessage.from_function(content=reply.content, name=function_name))
                #raise NameError(f"Function is not defined.")
        return responses
    
    
    
    # Defines a function to configure a trading bot based on commands and optional parameters.

    def set_trading_bot(self,command: str = None, params: str = None):
        if command == 'start':
            response = self.client.start()
            print(response)
        elif command == 'import_strategy':
            response = self.client.import_strategy(params)
        elif command == 'config':
            response = self.client.config(eval(params))
        elif command == 'status':
            response = self.client.status()
        elif command == 'history':
            response = self.client.history()
        elif command == 'stop':
            response = self.client.stop()
        else:
            response = {msg:"Invalid command"}
        return {"status": "completed", "command": command, "params": params, "response": response.msg}


    set_trading_bot_func = FunctionDeclaration(
            name="set_trading_bot",
            description="Set the trading bot with given command",
            parameters={
                "type_": "OBJECT",
                "properties": {
                    "command": {
                        "type_": "STRING",
                        "description": "commands to control trading bot, config parameters and query status and trade history",
                        "enum": [
                            "start",
                            "stop",
                            "status",
                            "import_strategy",
                            "config",
                            "history", 
                        ],
                    },
                    "params": {"type_": "STRING", "description": "optional parameters"},
                },
                "required": ["command"],
            },
        )


    def buildcode(self,desc : dict = None, params: str = None):  # noqa: ARG001
            return {"status": "completed"}
    buildcode_func = FunctionDeclaration(
            name="buildcode",
            description="build the code for trading",
            parameters={
                "type_": "OBJECT",
                "properties": {
                    "desc": {
                        "type_": "OBJECT",
                        "description": "JSON object containing optional parameters for trade code config",
                        "properties": {
                            # Example sub-properties within params
                            "id": {"type_": "STRING", "description": "Identifier for the trading "},
                            "trade_limit": {"type_": "NUMBER", "description": "Maximum number of trades to execute"},
                            "max_loss": {"type_": "NUMBER", "description": "Maximum loss tolerate"},
                            "indicator": {"type_": "STRING", "description": "technical indicator to follow"},
                            
                            # Add more properties as needed
                        }},
                    "params": {"type_": "STRING", "description": "optional parameters"},
                },
                "required": ["desc"],
            },
        )

    def getFTable(self):
        return [
            self.search_news_func,
            self.set_trading_bot_func,        
            self.buildcode_func,
            self.websearch_func
        ]




    #end function TAble
