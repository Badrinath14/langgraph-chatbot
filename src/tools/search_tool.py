# File: src/tools/search_tool.py

from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
import os
from dotenv import load_dotenv
from twilio.rest import Client

# Load variables from .env file
load_dotenv()

@tool
def send_whatsapp_message(message: str, phone_number: str) -> str:
    """
    Send a WhatsApp message using Twilio.
    Use this tool when user asks to send, share, or forward information via WhatsApp.
    
    Args:
        message: The complete message text to send (can be long, multi-line text)
        phone_number: Recipient's phone number with country code (e.g., +1234567890)
    
    Returns:
        Success or error message
    """
    try:
        # Get credentials
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        whatsapp_from = os.getenv("TWILIO_WHATSAPP_FROM")
        
        # Validate credentials
        if not all([account_sid, auth_token, whatsapp_from]):
            error_msg = "❌ Error: Missing Twilio credentials. Please set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_WHATSAPP_FROM in .env file"
            print(error_msg)
            return error_msg
        
        # Debug logging
        print(f"\n=== WhatsApp Tool Debug ===")
        print(f"Message length: {len(message)} characters")
        print(f"Phone number: {phone_number}")
        print(f"Message preview: {message[:100]}...")
        print(f"From number: {whatsapp_from}")
        
        # Initialize Twilio client
        client = Client(account_sid, auth_token)
        
        # Format phone number for WhatsApp
        to_number = phone_number.strip()
        if not to_number.startswith("whatsapp:"):
            to_number = f"whatsapp:{to_number}"
        
        # Ensure from number has whatsapp: prefix
        from_number = whatsapp_from
        if not from_number.startswith("whatsapp:"):
            from_number = f"whatsapp:{from_number}"
        
        # Clean and validate message
        message_to_send = str(message).strip()
        if not message_to_send:
            return "❌ Error: Message is empty"
        
        print(f"Sending to: {to_number}")
        print(f"Message to send: {message_to_send[:200]}...")
        
        # Send message
        twilio_message = client.messages.create(
            body=message_to_send,
            from_=from_number,
            to=to_number
        )
        
        success_msg = f"✅ WhatsApp message sent successfully to {phone_number}! Message SID: {twilio_message.sid}, Status: {twilio_message.status}"
        print(success_msg)
        print("=========================\n")
        
        return success_msg
    
    except Exception as e:
        error_msg = f"❌ Error sending WhatsApp message: {str(e)}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        return error_msg


def get_tools():
    """
    Return the list of tools to be used in the chatbot
    """
    tools = [
        TavilySearchResults(max_results=2),
        send_whatsapp_message
    ]
    return tools


def create_tool_node(tools):
    """
    Creates and returns a tool node for the graph
    """
    return ToolNode(tools=tools)