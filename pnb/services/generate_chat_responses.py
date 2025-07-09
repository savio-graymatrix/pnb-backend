# from typing import Optional
# from langgraph.prebuilt.chat_agent_executor import Prompt
# from langchain_core.messages import HumanMessage, AIMessageChunk
# import json
# from uuid import uuid4
# from pnb.langgraph.workflows import GRAPHS
# from pnb import LOGGER
# from typing import Any, Dict, List, Union
# from dataclasses import asdict, is_dataclass
# from pnb.services.chat_response_model import generate_event_response

# def serialise_ai_message_chunk(chunk):
#     if isinstance(chunk, AIMessageChunk):
#         return chunk.content
#     else:
#         raise TypeError(
#             f"Object of type {type(chunk).__name__} is not correctly formatted for serialisation"
#         )

# class CustomJSONEncoder(json.JSONEncoder):
#     def default(self, obj: Any) -> Any:
#         # Handle dataclasses (e.g., Supervisor, Command)
#         if is_dataclass(obj):
#             return asdict(obj)
#         # Handle custom message types (AIMessage, AIMessageChunk, HumanMessage, SystemMessage)
#         if hasattr(obj, '__dict__'):
#             data = obj.__dict__.copy()
#             # Include type information for clarity
#             data['__type__'] = obj.__class__.__name__
#             # Handle nested objects in additional_kwargs and response_metadata
#             for key, value in data.items():
#                 if isinstance(value, (dict, list)):
#                     data[key] = self._recursive_convert(value)
#             return data
#         # Fallback for other non-serializable types
#         try:
#             return json.JSONEncoder.default(self, obj)
#         except TypeError:
#             return str(obj)

#     def _recursive_convert(self, item: Any) -> Any:
#         # Recursively convert nested dictionaries and lists
#         if isinstance(item, dict):
#             return {k: self._recursive_convert(v) for k, v in item.items()}
#         elif isinstance(item, list):
#             return [self._recursive_convert(i) for i in item]
#         elif is_dataclass(item) or hasattr(item, '__dict__'):
#             return self.default(item)
#         return item

# async def generate_chat_responses(
#     message: str, checkpoint_id: Optional[str] = None, project_id: Optional[str] = None
# ):
#     is_new_conversation = checkpoint_id is None

#     if is_new_conversation:
#         # Generate new checkpoint ID for first message in conversation
#         new_checkpoint_id = str(uuid4())

#         config = {
#             "configurable": {"thread_id": new_checkpoint_id, "project_id": project_id},
#             "metadata": {
#                 "conversation_id": new_checkpoint_id,
#                 "user_message": (
#                     message[:100] + "..." if len(message) > 100 else message
#                 ),
#                 "is_new_conversation": True,
#                 "project_id": project_id,
#             },
#             "tags": ["perplexity-image-app", "new-conversation"],
#         }

#         # Initialize with first message
#         events = GRAPHS['chatbot'].astream_events(
#             {"messages": [HumanMessage(content=message)]},
#             version="v2",
#             config=config,
#             stream_mode="messages",
#         )

#         # First send the checkpoint ID
#         yield f'data: {{"type": "checkpoint", "checkpoint_id": "{new_checkpoint_id}"}}\n\n'
#     else:
#         config = {
#             "configurable": {"thread_id": checkpoint_id, "project_id": project_id},
#             "metadata": {
#                 "conversation_id": checkpoint_id,
#                 "user_message": (
#                     message[:100] + "..." if len(message) > 100 else message
#                 ),
#                 "is_new_conversation": False,
#                 "project_id": project_id,
#             },
#             "tags": ["perplexity-image-app", "continuing-conversation"],
#         }
#         # Continue existing conversation
#         events =  GRAPHS['chatbot'].astream_events(
#             {"messages": [HumanMessage(content=message)]},
#             version="v2",
#             config=config,
#             stream_mode="messages",
#         )

#     async for event in events:
#         response = await generate_event_response(event)
#         if len(response['data']) <= 0  :
#             continue
#         elif response['data']['node_type'] == "supervisor":
#             continue
#         elif response['data']['langgraph_node'] == None:
#             continue
#         else:
#             yield f"{json.dumps(response)}\n\n"
#     yield json.dumps({'data':{'type':'end'}}) + '\n\n'

#     # async for event in events:
#     #     LOGGER.debug(event)
#     #     event_type = event["event"]

#     #     if "metadata" in event:
#     #         if "langgraph_node" in event["metadata"]:
#     #             langgraph_node = event["metadata"]["langgraph_node"]
#     #         if "node_type" in event["metadata"]:
#     #             node_type = event["metadata"]["node_type"]

#     #     if event_type == "on_chat_model_stream":

#     #         if langgraph_node != "supervisor":
#     #             if node_type == "twitter_agent":

#     #                 chunk_content = serialise_ai_message_chunk(event["data"]["chunk"])
#     #                 json_data = json.dumps(
#     #                     {
#     #                         "type": "generating_tweet",
#     #                         "content": chunk_content,
#     #                         "langgraph_node": langgraph_node,
#     #                         "node_type": node_type,
#     #                     }
#     #                 )
#     #                 # write_debug_to_file("+++++ Event Start+++++")
#     #                 # write_debug_to_file(json_data)
#     #                 # write_debug_to_file("+++++ Event End+++++")
#     #                 yield f"data: {json_data}\n\n"
#     #             elif node_type in [
#     #                 "front_desk",
#     #                 "twitter_critic_agent",
#     #                 "instagram_critic_agent",
#     #                 "linkedin_article_critic_agent",
#     #                 "linkedin_post_critic_agent",
#     #             ]:
#     #                 chunk_content = serialise_ai_message_chunk(event["data"]["chunk"])
#     #                 json_data = json.dumps(
#     #                     {
#     #                         "type": "null",
#     #                         "content": chunk_content,
#     #                         "langgraph_node": langgraph_node,
#     #                         "node_type": node_type,
#     #                     }
#     #                 )
#     #                 yield f"data: {json_data}\n\n"
#     #             elif node_type == "image_agent":
#     #                 chunk_content = serialise_ai_message_chunk(event["data"]["chunk"])
#     #                 json_data = json.dumps(
#     #                     {
#     #                         "type": "image_generated",
#     #                         "content": chunk_content,
#     #                         "langgraph_node": langgraph_node,
#     #                         "node_type": node_type,
#     #                     }
#     #                 )
#     #                 yield f"data: {json_data}\n\n"
#     #             elif node_type == "instagram_agent":
#     #                 chunk_content = serialise_ai_message_chunk(event["data"]["chunk"])
#     #                 json_data = json.dumps(
#     #                     {
#     #                         "type": "instagram_generated",
#     #                         "content": chunk_content,
#     #                         "langgraph_node": langgraph_node,
#     #                         "node_type": node_type,
#     #                     }
#     #                 )
#     #                 yield f"data: {json_data}\n\n"
#     #             elif node_type == "linkedin_article_agent":
#     #                 chunk_content = serialise_ai_message_chunk(event["data"]["chunk"])
#     #                 json_data = json.dumps(
#     #                     {
#     #                         "type": "linkedin_article_generated",
#     #                         "content": chunk_content,
#     #                         "langgraph_node": langgraph_node,
#     #                         "node_type": node_type,
#     #                     }
#     #                 )
#     #                 yield f"data: {json_data}\n\n"
#     #             elif node_type == "linkedin_post_agent":
#     #                 chunk_content = serialise_ai_message_chunk(event["data"]["chunk"])
#     #                 json_data = json.dumps(
#     #                     {
#     #                         "type": "linkedin_post_generated",
#     #                         "content": chunk_content,
#     #                         "langgraph_node": langgraph_node,
#     #                         "node_type": node_type,
#     #                     }
#     #                 )
#     #                 yield f"data: {json_data}\n\n"
#     #             else:
#     #                 chunk_content = serialise_ai_message_chunk(event["data"]["chunk"])
#     #                 json_data = json.dumps(
#     #                     {
#     #                         "type": "content",
#     #                         "content": chunk_content,
#     #                         "langgraph_node": langgraph_node,
#     #                         "node_type": node_type,
#     #                     }
#     #                 )
#     #                 yield f"data: {json_data}\n\n"

#     #     elif event_type == "on_chat_model_end":
#     #         # Check if there are tool calls for search
#     #         tool_calls = (
#     #             event["data"]["output"].tool_calls
#     #             if hasattr(event["data"]["output"], "tool_calls")
#     #             else []
#     #         )
#     #         search_calls = [
#     #             call
#     #             for call in tool_calls
#     #             if call["name"] == "tavily_search"
#     #         ]
#     #         freepik_image_calls = [
#     #             call
#     #             for call in tool_calls
#     #             if call["name"] == "generate_imagen_image_tool"
#     #         ]

#     #         if search_calls:
#     #             # Signal that a search is starting
#     #             search_query = search_calls[0]["args"].get("query", "")
#     #             # Escape quotes and special characters
#     #             safe_query = (
#     #                 search_query.replace('"', '\\"')
#     #                 .replace("'", "\\'")
#     #                 .replace("\n", "\\n")
#     #             )
#     #             yield f'data: {{"type": "search_start", "query": "{safe_query}"}}\n\n'

#     #         elif freepik_image_calls:
#     #             # Signal that an image generation is starting
#     #             image_prompt = freepik_image_calls[0]["args"].get("prompt", "")
#     #             safe_prompt = (
#     #                 image_prompt.replace('"', '\\"')
#     #                 .replace("'", "\\'")
#     #                 .replace("\n", "\\n")
#     #             )
#     #             yield f'data: {{"type": "image_generation_start", "prompt": "{safe_prompt}"}}\n\n'

#     #     elif (
#     #         event_type == "on_tool_end" and event["name"] == "fetch_freepik_image_tool"
#     #     ):
#     #         # Image generation completed
#     #         output = event["data"]["output"]
#     #         if isinstance(output, dict) and "image_id" in output:
#     #             image_id = output["image_id"]
#     #             yield f'data: {{"type": "image_generated", "image_id": "{image_id}"}}\n\n'

#     #     elif (
#     #         event_type == "on_tool_end" and event["name"] == "upload_to_cloudinary_tool"
#     #     ):
#     #         # Image upload completed
#     #         output = event["data"]["output"]
#     #         if isinstance(output, str) and output.startswith("http"):
#     #             image_url = output
#     #             json_data = json.dumps(
#     #                 {"type": "image_uploaded", "url": image_url, "widget": "image"}
#     #             )
#     #             yield f"data: {json_data}\n\n"

#     #     elif (
#     #         event_type == "on_tool_end"
#     #         and event["name"] == "tavily_search"
#     #     ):
#     #         # Search completed - send results or error
#     #         output = event["data"]["output"]
#     #         urls = []

#     #         if (
#     #             hasattr(output, "content")
#     #             and isinstance(output.content, str)
#     #             and "results" in json.loads(output.content)
#     #         ):
#     #             # Extract URLs from the results list in the content
#     #             for item in json.loads(output.content)["results"]:
#     #                 if isinstance(item, dict) and "url" in item:
#     #                     urls.append(item["url"])
#     #         # Convert URLs to JSON and yield them if any were found
#     #         if urls:
#     #             urls_json = json.dumps(urls)
                
#     #             yield f'data: {{"type": "search_results", "urls": {urls_json}}}\n\n'

#     # # Wait for all tracers to complete if LangSmith is enabled
#     # if LANGCHAIN_TRACING_V2 and LANGCHAIN_API_KEY:
#     #     wait_for_all_tracers()

#     # # yielding an end event
#     # if node_type == "twitter_agent":
#     #     yield f'data: {{"type": "end", "agent": "twitter"}}\n\n'
#     # elif node_type == "image_agent":
#     #     yield f'data: {{"type": "end", "agent": "image"}}\n\n'
#     # elif node_type == "front_desk":
#     #     yield f'data: {{"type": "end", "agent": "front_desk"}}\n\n'
#     # elif node_type == "researcher":
#     #     yield f'data: {{"type": "end", "agent": "research"}}\n\n'
#     # elif node_type == "linkedin_article_agent":
#     #     yield f'data: {{"type": "end", "agent": "linkedin_article"}}\n\n'
#     # elif node_type == "linkedin_post_agent":
#     #     yield f'data: {{"type": "end", "agent": "linkedin_post"}}\n\n'
#     # elif node_type == "instagram_agent":
#     #     yield f'data: {{"type": "end", "agent": "instagram"}}\n\n'


from uuid import uuid4
from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage
from typing import Optional
from pnb.langgraph.workflows import GRAPHS
import json

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
        print(event)
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