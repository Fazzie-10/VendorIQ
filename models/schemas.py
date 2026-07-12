from pydantic import BaseModel
from typing import Optional


class GreenAPIWebhookPayload(BaseModel):
    typeWebhook: str
    instanceData: dict
    timestamp: Optional[int] = None
    idMessage: Optional[str] = None
    senderData: Optional[dict] = None
    messageData: Optional[dict] = None

    @property
    def sender_phone(self) -> str:
        if not self.senderData:
            return ""
        chat_id = self.senderData.get("chatId", "")
        return chat_id.replace("@c.us", "").replace("@g.us", "")

    @property
    def message_text(self) -> str:
        if not self.messageData:
            return ""
        msg_type = self.messageData.get("typeMessage", "")
        if msg_type == "textMessage":
            return (self.messageData.get("textMessageData", {}) or {}).get("textMessage", "").strip()
        if msg_type == "extendedTextMessage":
            return (self.messageData.get("extendedTextMessageData", {}) or {}).get("text", "").strip()
        return ""

    @property
    def is_voice_message(self) -> bool:
        if not self.messageData:
            return False
        return self.messageData.get("typeMessage", "") in ("voiceMessage", "audioMessage")

    @property
    def push_name(self) -> str:
        if not self.senderData:
            return ""
        return self.senderData.get("senderName", "") or self.senderData.get("chatName", "")

    @property
    def is_from_me(self) -> bool:
        return self.typeWebhook == "outgoingMessageReceived"

    @property
    def is_group(self) -> bool:
        if not self.senderData:
            return False
        chat_id = self.senderData.get("chatId", "")
        return "@g.us" in chat_id
