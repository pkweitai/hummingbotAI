import enum
from langchain.schema import AIMessage
from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import RunnableSequence
from langchain_core.prompts import HumanMessagePromptTemplate, ChatPromptTemplate
from typing import cast


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


def get_user_intent(ai_message: AIMessage) -> UserIntent:
    ai_answer: str = ai_message.content
    if "Greeting" in ai_answer:
        return UserIntent.Greeting
    elif "General status" in ai_answer:
        return UserIntent.GeneralStatus
    elif "Market information" in ai_answer:
        return UserIntent.MarketInformation
    elif "Portfolio information" in ai_answer:
        return UserIntent.PortfolioInformation
    elif "Price alerts" in ai_answer:
        return UserIntent.PriceAlerts
    elif "News alerts" in ai_answer:
        return UserIntent.NewsAlerts
    elif "Trading" in ai_answer:
        return UserIntent.Trading
    else:
        return UserIntent.Chat


def classify_user_intent_chain(llm: BaseChatModel) -> RunnableSequence:
    return cast(
        RunnableSequence,
        ChatPromptTemplate.from_messages([
            user_intent_classification_template(),
            HumanMessagePromptTemplate.from_template("{message}")]
        ) | llm | get_user_intent
    )
