from featuretable import HummingBotTools
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



class AiAgents:
       
    def __init__(self,BOTID) -> None:
        
        self.llm = GoogleAIGeminiChatGenerator(model="gemini-pro" );
        self.htable = HummingBotTools(BOTID,self.llm)

        llm4tool =GoogleAIGeminiChatGenerator(
                    model="gemini-pro",
                    tools=[Tool(function_declarations=self.htable.getFTable())]
        )
        self.pipeline = self.pipebuilder(llm4tool)


    def pipebuilder(self,llm):
        
        #Tool dispatch
        prompt_builder = DynamicChatPromptBuilder()
        # Create and configure the pipeline
        pipelinex = Pipeline()
        pipelinex.add_component("prompt_builder", prompt_builder)
        pipelinex.add_component("llm", llm)
        pipelinex.connect("prompt_builder.prompt", "llm.messages")
        return pipelinex



    def chat_with_agent(self,user_input):
        # Run the pipeline to determine the action and tool response
        messages = [ChatMessage.from_user(content=user_input)]
        res = self.pipeline.run(data=
                        {"prompt_builder": {
                                "template_variables":{"location": "Mexico",
                                                    "command" : "start" ,
                                                    "desc" : " " 
                                                    },
                                "prompt_source": messages}})

        print(res)

        tool_messages = self.htable.dispatch(res["llm"]["replies"])
        if(tool_messages and tool_messages[0].name is None):
            message = tool_messages[0].content 
            return { "msg" :message, "status" : 0}
        else:
            # complete message from tool responses
            messages += res["llm"]["replies"] + tool_messages
            print(messages)
            print("\n\n")
            print(tool_messages)
            res = self.llm.run(messages=messages)
            contents= self.dumpcontents(res["replies"])
            return { "msg" : contents[0], "status" : 1}
        
    
    def dumpcontents(self,res): 
            contents=[]
            for item in res:
                contents.append(item.content)
            return contents