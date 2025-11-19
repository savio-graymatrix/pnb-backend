from langchain_core.tools import tool
import re


@tool
def pan_tool(pan_number: str):

    """Tool to check the pan number

    Verify if a PAN number follows the standard Indian PAN format (5 letters, 4 digits, 1 letter).
    
    
    Args:
        pan_number (str): The PAN number to validate (e.g., "ABCDE1234F").
        
    Returns:
        bool: True if the PAN number matches the valid format, False otherwise.
    """
    # Define the PAN format pattern: 5 uppercase letters, 4 digits, 1 uppercase letter
    pan_pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
    
    # Check if the input matches the pattern
    if pan_number and re.match(pan_pattern, pan_number):
        return True
    return False