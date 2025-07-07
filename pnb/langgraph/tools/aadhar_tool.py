from langchain_core.tools import tool
import re

@tool
def aadhar_tool(aadhar_number: str):
    """
    Verify if an Aadhar number follows the standard Indian Aadhar format (12-digit numeric string).
    
    Args:
        aadhar_number (str): The Aadhar number to validate (e.g., "123456789012").
        
    Returns:
        bool: True if the Aadhar number matches the valid format, False otherwise.
    """
    # Define the Aadhar format pattern: 12 digits
    aadhar_pattern = r'^\d{12}$'
    
    # Check if the input matches the pattern
    if aadhar_number and re.match(aadhar_pattern, aadhar_number):
        return True
    return False
