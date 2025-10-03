# File: src/tools/search_tool.py

from langchain_tavily import TavilySearch
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
        message: The message text to send
        phone_number: Recipient's phone number with country code (e.g., +1234567890)
    
    Returns:
        Success or error message
    """
    try:
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        whatsapp_from = os.getenv("TWILIO_WHATSAPP_FROM")  # Format: whatsapp:+14155238886
        
        if not all([account_sid, auth_token, whatsapp_from]):
            return "❌ Error: Missing Twilio credentials. Please set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_WHATSAPP_FROM in .env file"
        
        client = Client(account_sid, auth_token)
        
        # Format phone number for WhatsApp
        if not phone_number.startswith("whatsapp:"):
            phone_number = f"whatsapp:{phone_number}"
        
        # Send message
        twilio_message = client.messages.create(
            body=message,
            from_=whatsapp_from,
            to=phone_number
        )
        
        return f"✅ WhatsApp message sent successfully to {phone_number}! Message SID: {twilio_message.sid}"
    
    except Exception as e:
        return f"❌ Error sending WhatsApp message: {str(e)}"


def get_tools():
    """
    Return the list of tools to be used in the chatbot
    """
    tools = [
        TavilySearch(max_results=2),
        send_whatsapp_message
    ]
    return tools


def create_tool_node(tools):
    """
    Creates and returns a tool node for the graph
    """
    return ToolNode(tools=tools)