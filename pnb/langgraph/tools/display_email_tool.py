from langchain.tools import tool


@tool
async def display_email_tool(markdown_text: str):
    """
    Tool to display the email in a specialized widget at the frontend

    Args:
        makrdown_text (str): The markdown text of the mail to display

    Returns:
        str: The markdown text of the mail to display
    """
    return markdown_text
