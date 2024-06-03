import functools
from langchain.schema import SystemMessage
from os.path import realpath, join


def template_path() -> str:
    return realpath(join(__file__, "../"))


@functools.lru_cache
def user_intent_classification() -> SystemMessage:
    with open(join(template_path(), "user_intent_classification.md"), "r") as fd:
        return SystemMessage(content=fd.read())
