from langchain.tools import tool


@tool
async def whatsapp_display_tool(markdown_text: str):
    """
    Tool used to display a whataspp curated message

    Args:
        markdown_text (str): The markdown text to display

    Returns:
        str: The markdown text to display
    """
    return markdown_text
