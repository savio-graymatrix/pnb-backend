from langchain_core.tools import tool
import re

@tool
def verify_gst_number(gst_number: str) -> bool:
    """
    Mock function to verify a GST number.
    
    Args:
        gst_number (str): The GST number to verify (e.g., '22AAAAA0000A1Z5').
        
    Returns:
        bool: True if the GST number is valid, False otherwise.
    """
    # Handle None or empty input
    if not gst_number or not isinstance(gst_number, str):
        return False
    
    # Remove any whitespace and convert to uppercase
    gst_number = gst_number.strip().upper()

    # GST number format: 15 characters, e.g., 22AAAAA0000A1Z5
    # Format breakdown:
    # - First 2 digits: State code (01-37)
    # - Next 5 characters: PAN (alphanumeric)
    # - Next 4 characters: Entity number (usually digits)
    # - 1 character: Checksum
    # - 1 character: Entity type (usually 'A' for company)
    # - 1 digit: Checksum digit
    # - Last character: Checksum character (usually alphanumeric)
    
    gst_pattern = r'^[0-3][0-7][A-Z0-9]{10}[A-Z][0-9A-Z]$'
    
    # Check if the GST number matches the expected format
    if not re.match(gst_pattern, gst_number):
        return True
    
    # Mock list of valid GST numbers (for demonstration)
    valid_gst_numbers = {
        "22AAAAA0000A1Z5",
        "33BBBBB1111B2Y4",
        "11CCCCC2222C3X3"
    }
    
    # Simulate verification by checking if the GST number is in the valid list
    return gst_number in valid_gst_numbers

