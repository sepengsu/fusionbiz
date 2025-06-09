# rag_engine/utils/history.py

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage
from typing import List


class InMemoryChatHistory(BaseChatMessageHistory):
    def __init__(self, session_id: str = "default"):
        self.messages: List[BaseMessage] = []

    def add_message(self, message: BaseMessage) -> None:
        self.messages.append(message)

    def clear(self) -> None:
        self.messages = []

    def get_messages(self) -> List[BaseMessage]:
        return self.messages

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

def format_chat_history(messages):
    formatted = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            formatted.append(f"사용자: {msg.content}")
        elif isinstance(msg, AIMessage):
            formatted.append(f"AI: {msg.content}")
        elif isinstance(msg, SystemMessage):
            formatted.append(f"(시스템): {msg.content}")
        else:
            formatted.append(f"(알 수 없음): {msg.content}")
    return "\n".join(formatted)
