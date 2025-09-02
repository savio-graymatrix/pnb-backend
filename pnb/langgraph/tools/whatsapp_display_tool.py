from langchain.tools import tool


@tool
async def whatsapp_display_tool(text: str):
    """
    Tool used to display a whataspp curated message

    Args:
        text (str): The text to display

    Returns:
        str: The text to display
    """
    return text
