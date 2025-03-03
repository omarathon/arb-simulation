from typing import Literal, Union
from pydantic import BaseModel
from backend.shared.redis import OddsUpdateMessage, ArbMessage

# 🔹 Strongly Typed WebSocket Message
class WebSocketMessage(BaseModel):
    message_type: Literal["odds_update", "arb_detection", "arb_execution"]
    contents: Union[OddsUpdateMessage, ArbMessage]
