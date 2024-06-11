import enum
from langchain.schema import AIMessage
from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import RunnableSequence
from langchain_core.prompts import HumanMessagePromptTemplate, ChatPromptTemplate
from typing import cast,List
import re


from hummingbot_ai.prompt_templates import user_intent_classification_template


class UserIntent(enum.Enum):
    Greeting = 1
    GeneralStatus = 2
    MarketInformation = 3
    PortfolioInformation = 4
    PriceAlerts = 5
    NewsAlerts = 6
    Trading = 7
    Chat = 8
 

def extract_parameters(message: str) -> List[str]:
    # Use regex to find the parameters part
    match = re.search(r'parameters: \[(.*?)\]', message)
    if not match:
        return []

    # Extract the parameters and split them into a list
    params_str = match.group(1)
    params_list = re.findall(r'"(.*?)"', params_str)
    return params_list


def get_user_intent(ai_message: AIMessage) -> UserIntent:
    ai_answer: str = ai_message.content
    print("\nraw ai answers: --> " +ai_answer)
    if "Greeting" in ai_answer:
        intent= UserIntent.Greeting
    elif "General status" in ai_answer:
        intent= UserIntent.GeneralStatus
    elif "Market information" in ai_answer:
        intent= UserIntent.MarketInformation
    elif "Portfolio information" in ai_answer:
        intent= UserIntent.PortfolioInformation
    elif "Price alerts" in ai_answer:
        intent= UserIntent.PriceAlerts
    elif "News alerts" in ai_answer:
        intent= UserIntent.NewsAlerts
    elif "Trading" in ai_answer:
        intent= UserIntent.Trading
    else:
        intent= UserIntent.Chat
    
    params = extract_parameters(ai_answer)

    return intent,params,ai_answer


def classify_user_intent_chain(llm: BaseChatModel) -> RunnableSequence:
    return cast(
        RunnableSequence,
        ChatPromptTemplate.from_messages([
            user_intent_classification_template(),
            HumanMessagePromptTemplate.from_template("{message}")]
        ) | llm | get_user_intent
    )
