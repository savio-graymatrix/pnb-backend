from uuid import uuid4
from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage
from typing import Optional
from pnb.langgraph.workflows import GRAPHS
import json
from pnb import LOGGER

def serialise_ai_message_chunk(chunk): 
    if(isinstance(chunk, AIMessageChunk)):
        return chunk.content
    else:
        raise TypeError(
            f"Object of type {type(chunk).__name__} is not correctly formatted for serialisation"
        )

async def generate_chat_responses(message: str, checkpoint_id: Optional[str] = None):
    is_new_conversation = checkpoint_id is None
    
    if is_new_conversation:
        # Generate new checkpoint ID for first message in conversation
        new_checkpoint_id = str(uuid4())

        config = {
            "configurable": {
                "thread_id": new_checkpoint_id,
                "project_id": "68628d545384d01e747d6b79"
            }
        }
        
        # Initialize with first message
        events = GRAPHS['chatbot'].astream_events(
            {"messages": [HumanMessage(content=message)]},
            version="v2",
            config=config
        )
        
        # First send the checkpoint ID
        yield f"data: {{\"type\": \"checkpoint\", \"checkpoint_id\": \"{new_checkpoint_id}\"}}\n\n"
    else:
        config = {
            "configurable": {
                "thread_id": checkpoint_id
            }
        }
        # Continue existing conversation
        events = GRAPHS['chatbot'].astream_events(
            {"messages": [HumanMessage(content=message)]},
            version="v2",
            config=config
        )

    async for event in events:
        event_type = event["event"]
        LOGGER.debug(event)
        if event_type in ["on_tool_end","on_tool_start"]:
            continue
        if event_type in ["on_chat_model_stream","on_chat_model_end"]:
            if "chunk" not in event['data']:
                continue
            
            chunk_content = serialise_ai_message_chunk(event["data"]["chunk"])
            safe_content = chunk_content.replace("'", "\\'").replace("\n", "\\n")
            if safe_content == "":
                continue
            yield f"data: {{\"type\": \"content\", \"content\": \"{safe_content}\"}}\n\n"
    # Send an end event
    yield f"data: {{\"type\": \"end\"}}\n\n"