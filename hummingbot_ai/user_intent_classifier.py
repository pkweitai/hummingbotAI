import enum
from langchain_core.language_models import BaseChatModel
from langchain.schema import (
    AIMessage,
    HumanMessage,
)
from typing import cast

from hummingbot_ai.prompt_templates import user_intent_classification


class UserIntent(enum.Enum):
    Greeting = 1
    GeneralStatus = 2
    MarketInformation = 3
    PortfolioInformation = 4
    PriceAlerts = 5
    NewsAlerts = 6
    Trading = 7
    Chat = 8


async def get_user_intent(chat_model: BaseChatModel, user_message: str) -> UserIntent:
    ai_message: AIMessage = cast(
        AIMessage,
        await chat_model.ainvoke([user_intent_classification(), HumanMessage(content=user_message)]),
    )
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