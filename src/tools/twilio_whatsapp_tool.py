# File: src/tools/twilio_whatsapp_tool.py

from langchain.tools import BaseTool
from typing import Optional, Type
from pydantic import BaseModel, Field
from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

class WhatsAppInput(BaseModel):
    """Input schema for WhatsApp tool"""
    message: str = Field(description="The message to send via WhatsApp")
    phone_number: str = Field(description="The recipient's phone number in format: +1234567890")

class TwilioWhatsAppTool(BaseTool):
    """Tool for sending messages via WhatsApp using Twilio"""
    
    name: str = "send_whatsapp_message"
    description: str = """
    Useful for sending messages to someone via WhatsApp.
    Input should be the message text and the recipient's phone number.
    Phone number must include country code (e.g., +1234567890).
    Use this when user asks to send a message, share information, or notify someone via WhatsApp.
    """
    args_schema: Type[BaseModel] = WhatsAppInput
    
    def __init__(self):
        super().__init__()
        # Initialize Twilio client
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.whatsapp_from = os.getenv("TWILIO_WHATSAPP_FROM")  # Format: whatsapp:+14155238886
        
        if not all([self.account_sid, self.auth_token, self.whatsapp_from]):
            raise ValueError("Missing Twilio credentials in environment variables")
        
        self.client = Client(self.account_sid, self.auth_token)
    
    def _run(self, message: str, phone_number: str) -> str:
        """Send WhatsApp message"""
        try:
            # Format phone number for WhatsApp
            if not phone_number.startswith("whatsapp:"):
                phone_number = f"whatsapp:{phone_number}"
            
            # Send message
            twilio_message = self.client.messages.create(
                body=message,
                from_=self.whatsapp_from,
                to=phone_number
            )
            
            return f"✅ WhatsApp message sent successfully! Message SID: {twilio_message.sid}"
        
        except Exception as e:
            return f"❌ Error sending WhatsApp message: {str(e)}"
    
    async def _arun(self, message: str, phone_number: str) -> str:
        """Async version - not implemented"""
        raise NotImplementedError("Async not supported for this tool")


# Alternative: Simple function-based tool
def send_whatsapp_message(message: str, phone_number: str) -> str:
    """
    Send a WhatsApp message using Twilio.
    
    Args:
        message: The message text to send
        phone_number: Recipient's phone number with country code (e.g., +1234567890)
    
    Returns:
        Success or error message
    """
    try:
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        whatsapp_from = os.getenv("TWILIO_WHATSAPP_FROM")
        
        if not all([account_sid, auth_token, whatsapp_from]):
            return "❌ Error: Missing Twilio credentials in environment variables"
        
        client = Client(account_sid, auth_token)
        
        # Format phone number
        if not phone_number.startswith("whatsapp:"):
            phone_number = f"whatsapp:{phone_number}"
        
        # Send message
        twilio_message = client.messages.create(
            body=message,
            from_=whatsapp_from,
            to=phone_number
        )
        
        return f"✅ WhatsApp message sent successfully! Message SID: {twilio_message.sid}"
    
    except Exception as e:
        return f"❌ Error sending WhatsApp message: {str(e)}"