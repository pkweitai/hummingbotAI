import functools
from os.path import realpath, join

from langchain_core.prompts import SystemMessagePromptTemplate


def template_path() -> str:
    return realpath(join(__file__, "../"))


@functools.lru_cache
def user_intent_classification_template() -> SystemMessagePromptTemplate:
    with open(join(template_path(), "user_intent_classification.md"), "r") as fd:
        return SystemMessagePromptTemplate.from_template(fd.read())



@functools.lru_cache
def user_general_chat_template() -> SystemMessagePromptTemplate:
    with open(join(template_path(), "user_generalchat.md"), "r") as fd:
        return SystemMessagePromptTemplate.from_template(fd.read())
