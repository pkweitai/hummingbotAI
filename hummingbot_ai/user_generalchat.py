import enum
from langchain.schema import AIMessage
from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import RunnableSequence
from langchain_core.prompts import HumanMessagePromptTemplate, ChatPromptTemplate
from typing import cast


from hummingbot_ai.prompt_templates import user_general_chat_template




def get_response(ai_message: AIMessage) -> str:
    ai_answer: str = ai_message.content
    return ai_answer 


def response_user_generalchat(llm: BaseChatModel) -> RunnableSequence:
    return cast(
        RunnableSequence,
        ChatPromptTemplate.from_messages([
            user_general_chat_template(),
            HumanMessagePromptTemplate.from_template("{message}")]
        ) | llm | get_response
    )
