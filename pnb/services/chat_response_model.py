from pydantic import Field, BaseModel
from langchain_core.messages import AIMessageChunk
import json
from pnb import LOGGER

# class Chatresponse['data'](BaseModel):
#     type: Field()
#     content: Field()
#     langgraph_node: Field("generated_structured_response['data']s | agent")
#     node_type: Field()


def serialise_ai_message_chunk(chunk):
    if isinstance(chunk, AIMessageChunk):
        return chunk.content
    else:
        raise TypeError(
            f"Object of type {type(chunk).__name__} is not correctly formatted for serialisation"
        )


AGENT_ACTIONS = {
    # "twitter_agent": "generating_tweet",
    # "front_desk": "null",
    # "twitter_critic_agent": "null",
    # "instagram_critic_agent": "null",
    # "linkedin_article_critic_agent": "null",
    # "linkedin_post_critic_agent": "null",
    # "image_agent": "image_generated",
    # "instagram_agent": "instagram_generated",
    # "linkedin_article_agent": "linkedin_article_generated",
    # "linkedin_post_agent": "linkedin_post_generated",
    # "navigation_agent": "null   ",
    "chatbot":"chatbot",
    "default": "content",
}

TOOL_ACTIONS = {
    # "tavily_search": {"start": "search_start", "end": "search_results",'fetch_key': "query"},
    # "generate_imagen_image_tool": {
    #     "start": "image_generation_start",
    #     "end": "image_generated",
    #     'fetch_key': "prompt"
    # },
    # "upload_to_cloudinary_tool": {"start": None, "end": "image_uploaded"},
}

def safe_parser(text: str) -> str:
    return (text.replace('"', '\\"')
            .replace("'", "\\'")
            .replace("\n", "\\n"))

async def generate_event_response(event: dict) -> dict:
    """
    Converts the Event dictionary into Chatresponse['data'] Object

    :params:
    event (dict): Event data

    :returns:
    Chatresponse['data']

    :raises:
    """
    response=  {"data": {
        "content": "",
        "langgraph_node": None,
        "node_type": None
    }}
    if "metadata" in event:
        if "langgraph_node" in event["metadata"]:
            response['data'].update({"langgraph_node": event["metadata"]["langgraph_node"]})
        if "node_type" in event["metadata"]:
            response['data'].update({"node_type": event["metadata"]["node_type"]})
   
    match (event["event"]):
        case "on_chat_model_stream":
            if response['data']["langgraph_node"] != "supervisor":
                # match(response['data']["node_type"]):
                #     case "twitter_agent":
                response['data'].update(
                    {"content": serialise_ai_message_chunk(event["data"]["chunk"])}
                )
                if response['data']["node_type"] in AGENT_ACTIONS:
                    response['data'].update({"type": AGENT_ACTIONS[response['data']["node_type"]]})
                    # return response['data']
                else:
                    response['data'].update({"type": AGENT_ACTIONS["default"]})
            return response
        case "on_chat_model_end":
            del response['data']['content']
            tool_calls = (
                event["data"]["output"].tool_calls
                if hasattr(event["data"]["output"], "tool_calls")
                else []
            )
            segregated_tool_calls = dict()
            for key in TOOL_ACTIONS:
                segregated_tool_calls.update(
                    {key: [call for call in tool_calls if call["name"] == key]}
                )
                if len(segregated_tool_calls[key]) > 0 and key not in ["upload_to_cloudinary_tool"]:
                    query = segregated_tool_calls[key][0]["args"].get(TOOL_ACTIONS[key]['fetch_key'], "")
                    response['data'].update({
                        "type": TOOL_ACTIONS[key]['start'],
                        TOOL_ACTIONS[key]['fetch_key'] : safe_parser(query)
                    })
                    return response
        case "on_tool_end":
            del response['data']['content']
            match (event["name"]):
                case "generate_imagen_image_tool":
                    output = event["data"]["output"]
                    if isinstance(output, dict) and "image_id" in output:
                        image_id = output["image_id"]
                        response['data'].update(
                            {
                                "type": TOOL_ACTIONS["generate_imagen_image_tool"][
                                    "end"
                                ],
                                "image_id": image_id,
                            }
                        )
                        return response
                case "tavily_search":
                    output = event["data"]["output"]
                    urls = []

                    if (
                        hasattr(output, "content")
                        and isinstance(output.content, str)
                        and "results" in json.loads(output.content)
                    ):
                        # Extract URLs from the results list in the content
                        for item in json.loads(output.content)["results"]:
                            if isinstance(item, dict) and "url" in item:
                                urls.append(item["url"])
                    # Convert URLs to JSON and yield them if any were found
                    if urls:
                        # urls_json = json.dumps(urls)
                        response['data'].update(
                            {
                                "type": TOOL_ACTIONS["tavily_search"]["end"],
                                "urls": urls,
                            }
                        )
                        return response
                

    return response

    # end, generating_tweet, null, image_generated, instagram_genetrated, linkedin_article_generated, linkedin_post_generated, content, search_start, image_generation_start, search_results
