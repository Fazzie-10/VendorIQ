from pydantic import BaseModel
from typing import Optional


class GreenAPIWebhookPayload(BaseModel):
    typeWebhook: str
    instanceData: dict
    timestamp: int
    idMessage: str
    senderData: dict
    messageData: dict

    @property
    def sender_phone(self) -> str:
        chat_id = self.senderData.get("chatId", "")
        return chat_id.replace("@c.us", "").replace("@g.us", "")

    @property
    def message_text(self) -> str:
        msg_type = self.messageData.get("typeMessage", "")
        if msg_type == "textMessage":
            return (self.messageData.get("textMessageData", {}) or {}).get("textMessage", "")
        return ""

    @property
    def push_name(self) -> str:
        return self.senderData.get("senderName", "")

    @property
    def is_from_me(self) -> bool:
        return self.typeWebhook == "outgoingMessageReceived"

    @property
    def is_group(self) -> bool:
        chat_id = self.senderData.get("chatId", "")
        return "@g.us" in chat_id
