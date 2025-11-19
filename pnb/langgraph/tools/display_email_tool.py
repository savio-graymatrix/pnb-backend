from langchain.tools import tool


@tool
async def display_email_tool(text: str):
    """
    Tool to display the email in a specialized widget at the frontend

    Args:
        text (str): The HTML text of the mail to display

    Returns:
        str: The HTML text of the mail to display
    """
    return text
