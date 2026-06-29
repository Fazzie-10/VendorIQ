from pydantic import BaseModel
from typing import Optional


class EvolutionWebhookPayload(BaseModel):
    event: str
    instance: str
    data: dict

    @property
    def sender_phone(self) -> str:
        jid = self.data.get("key", {}).get("remoteJid", "")
        return jid.replace("@s.whatsapp.net", "").replace("@g.us", "")

    @property
    def message_text(self) -> str:
        msg = self.data.get("message", {})
        return (
            msg.get("conversation")
            or msg.get("extendedTextMessage", {}).get("text")
            or ""
        ).strip()

    @property
    def push_name(self) -> str:
        return self.data.get("pushName", "")

    @property
    def is_from_me(self) -> bool:
        return self.data.get("key", {}).get("fromMe", False)

    @property
    def is_group(self) -> bool:
        jid = self.data.get("key", {}).get("remoteJid", "")
        return "@g.us" in jid
