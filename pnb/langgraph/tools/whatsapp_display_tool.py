from langchain.tools import tool


@tool
async def whatsapp_display_tool(markdown_text: str):
    """
    Tool used to display a whataspp curated message

    Args:
        markdown_text (str): The markdown text to display. Strictly use markdown rules here.
        Example: data: **Hello Sam,**\n\nWe appreciate your interest in our Standard Home Loan offering. At T Solutions, we are committed to helping you achieve your homeownership goals with tailored solutions, competitive rates, and expert guidance every step of the way.\n\n🏡 **Why choose T Solution’s Home Loan?**\n- Attractive interest rates\n- Flexible repayment options\n- Personalized support from our specialists\n\nIf you’d like to discuss your options or have any questions, simply reply to this message. We’re here to assist you!\n\n**Best regards,\nT Solutions Team**

    Returns:
        str: The markdown text to display
    """
    return markdown_text
