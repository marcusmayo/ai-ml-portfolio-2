"""
Email service using Resend
Sends welcome emails with itineraries
"""
import os
from typing import Dict
import resend

# Initialize Resend with API key from environment
resend.api_key = os.getenv("RESEND_API_KEY")

def send_itinerary_email(
    to_email: str,
    vibe: str,
    itinerary: Dict[str, str],
    lead_id: str
) -> bool:
    """Send welcome email with personalized itinerary"""
    
    # Vibe-specific subject lines
    subject_lines = {
        "chill": "Your Chill Paradise Awaits in Costambar 🧘",
        "adventure": "Your Adventure Itinerary is Ready! 🏄",
        "music": "Get Ready to Dance in Costambar! 🎵",
        "wellness": "Your Wellness Retreat Awaits 🌺",
        "luxe": "Your Luxury Escape to Paradise 💎"
    }
    
    subject = subject_lines.get(vibe, "Your Perfect Costambar Itinerary 🌴")
    
    # HTML email template (same as before)
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #F0F8FF;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff;">
            <div style="background: linear-gradient(135deg, #4ECDC4 0%, #006994 100%); padding: 40px 20px; text-align: center;">
                <h1 style="color: #ffffff; margin: 0; font-size: 32px;">Your Paradise Awaits! 🌴</h1>
                <p style="color: #ffffff; margin: 10px 0 0 0; font-size: 18px;">Your personalized Costambar itinerary</p>
            </div>
            
            <div style="padding: 40px 20px;">
                <p style="color: #2C3E50; font-size: 16px; line-height: 1.6;">
                    Hello from Your Paradise! 👋
                </p>
                
                <p style="color: #2C3E50; font-size: 16px; line-height: 1.6;">
                    We've created a perfect 2-day experience just for you based on your <strong>{vibe}</strong> vibe.
                </p>
                
                <div style="background-color: #E8F8F5; border-left: 4px solid #4ECDC4; padding: 20px; margin: 20px 0; border-radius: 5px;">
                    <h2 style="color: #006994; margin: 0 0 10px 0; font-size: 24px;">☀️ Day 1</h2>
                    <p style="color: #2C3E50; font-size: 16px; line-height: 1.6; margin: 0;">
                        {itinerary.get('day_1', '')}
                    </p>
                </div>
                
                <div style="background-color: #FFF9E6; border-left: 4px solid #FFD700; padding: 20px; margin: 20px 0; border-radius: 5px;">
                    <h2 style="color: #006994; margin: 0 0 10px 0; font-size: 24px;">🌅 Day 2</h2>
                    <p style="color: #2C3E50; font-size: 16px; line-height: 1.6; margin: 0;">
                        {itinerary.get('day_2', '')}
                    </p>
                </div>
                
                <div style="text-align: center; margin: 40px 0;">
                    <a href="https://welcometoyourdominicanparadise.com?utm_source=email&utm_medium=itinerary&utm_campaign=quiz&lead_id={lead_id}" 
                       style="display: inline-block; background-color: #FFD700; color: #2C3E50; text-decoration: none; padding: 16px 40px; border-radius: 8px; font-size: 18px; font-weight: bold;">
                        Book Your Stay Now
                    </a>
                </div>
                
                <p style="color: #2C3E50; font-size: 16px; line-height: 1.6;">
                    Ready to make it happen? We're here to help!
                </p>
                
                <div style="background-color: #F8F9FA; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="color: #006994; margin: 0 0 10px 0; font-size: 18px;">Contact Us</h3>
                    <p style="color: #2C3E50; font-size: 14px; line-height: 1.6; margin: 5px 0;">
                        📧 Email: <a href="mailto:welcometomyparadisedr@gmail.com" style="color: #4ECDC4;">welcometomyparadisedr@gmail.com</a>
                    </p>
                    <p style="color: #2C3E50; font-size: 14px; line-height: 1.6; margin: 5px 0;">
                        📱 Dale: <a href="https://wa.me/16142965583" style="color: #4ECDC4;">+1 614-296-5583</a> (WhatsApp)
                    </p>
                    <p style="color: #2C3E50; font-size: 14px; line-height: 1.6; margin: 5px 0;">
                        📱 Danielle: <a href="https://wa.me/16142455192" style="color: #4ECDC4;">+1 614-245-5192</a>
                    </p>
                </div>
            </div>
            
            <div style="background-color: #2C3E50; color: #ffffff; padding: 20px; text-align: center; font-size: 14px;">
                <p style="margin: 0 0 10px 0;">
                    💕 Black-owned | Romance-friendly | Alternative lifestyles welcomed
                </p>
                <p style="margin: 0; color: #B0B0B0;">
                    Your Paradise - Costambar, Puerto Plata, Dominican Republic
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
Your Paradise Awaits!

Hello from Your Paradise!

We've created a perfect 2-day experience just for you based on your {vibe} vibe.

DAY 1:
{itinerary.get('day_1', '')}

DAY 2:
{itinerary.get('day_2', '')}

Book your stay: https://welcometoyourdominicanparadise.com

Contact us:
- Email: welcometomyparadisedr@gmail.com
- Dale: +1 614-296-5583 (WhatsApp)
- Danielle: +1 614-245-5192

Black-owned | Romance-friendly | Alternative lifestyles welcomed
Your Paradise - Costambar, Puerto Plata, Dominican Republic
    """
    
    try:
        # IMPORTANT: Use Resend's test domain (no setup needed!)
        params = {
            "from": "Your Paradise <onboarding@resend.dev>",
            "to": [to_email],
            "subject": subject,
            "html": html_content,
            "text": text_content,
            "reply_to": "welcometomyparadisedr@gmail.com",  # Replies go to your real email!
            "tags": [
                {"name": "category", "value": "itinerary"},
                {"name": "vibe", "value": vibe},
                {"name": "lead_id", "value": lead_id}
            ]
        }
        
        response = resend.Emails.send(params)
        print(f"Email sent successfully to {to_email}. ID: {response.get('id')}")
        return True
        
    except Exception as e:
        print(f"Failed to send email to {to_email}: {str(e)}")
        return False
