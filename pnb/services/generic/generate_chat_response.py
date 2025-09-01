from uuid import uuid4
from langchain_core.messages import AIMessageChunk, HumanMessage
from typing import Optional
from fastapi import HTTPException
from langgraph.graph.state import CompiledStateGraph
from pnb import LOGGER


def serialise_ai_message_chunk(chunk):
    if isinstance(chunk, AIMessageChunk):
        return chunk.content
    else:
        raise TypeError(
            f"Object of type {type(chunk).__name__} is not correctly formatted for serialisation"
        )


async def generate_chat_responses(
    graph: CompiledStateGraph,
    message: str,
    checkpoint_id: Optional[str] = None,
    checkpoint_required: bool = False,
):
    is_new_conversation = checkpoint_id is None

    if is_new_conversation and checkpoint_required:
        raise HTTPException(
            status_code=400,
            detail="Checkpoint ID is required for existing conversations",
        )
    if is_new_conversation:
        # Generate new checkpoint ID for first message in conversation
        new_checkpoint_id = str(uuid4())

        config = {"configurable": {"thread_id": new_checkpoint_id}}

        # Initialize with first message
        events = graph.astream_events(
            {"messages": [HumanMessage(content=message)]}, version="v2", config=config
        )

        # First send the checkpoint ID
        yield f'data: {{"type": "checkpoint", "checkpoint_id": "{new_checkpoint_id}"}}\n\n'
    else:

        config = {"configurable": {"thread_id": checkpoint_id}}
        # Continue existing conversation
        events = graph.astream_events(
            {"messages": [HumanMessage(content=message)]}, version="v2", config=config
        )

    async for event in events:
        # LOGGER.debug(event)
        event_type = event["event"]
        if event_type == "on_tool_start":
            continue
        if event_type == "on_tool_end":
            if event["name"] == "whatsapp_display_tool":
                yield f'data: {{"type": "whatsapp", "content": "{event["data"]["output"].content}"}}\n\n'
            continue
        if event_type == "langgraph_node" and event["langgraph_node"] == "tools":
            continue
        if event_type in ["on_chat_model_stream", "on_chat_model_end"]:

            if "chunk" not in event["data"]:
                continue
            if (
                "langgraph_node" in event["metadata"]
                and event["metadata"]["langgraph_node"] == "tools"
            ):
                continue
            chunk_content = serialise_ai_message_chunk(event["data"]["chunk"])
            safe_content = chunk_content.replace("'", "\\'").replace("\n", "\\n")
            if safe_content == "":
                continue
            yield f'data: {{"type": "content", "content": "{safe_content}"}}\n\n'
    # Send an end event
    yield f'data: {{"type": "end"}}\n\n'
