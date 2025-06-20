"""State management for the DataAgent."""

from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage

class InputState(BaseModel):
    """Input state for the DataAgent."""
    messages: List[BaseMessage] = Field(
        default_factory=list,
        description="The conversation messages"
    )

class State(BaseModel):
    """State for the DataAgent."""
    messages: List[BaseMessage] = Field(
        default_factory=list,
        description="The conversation messages"
    )
    is_last_step: bool = Field(
        default=False,
        description="Whether this is the last step in the conversation"
    ) 