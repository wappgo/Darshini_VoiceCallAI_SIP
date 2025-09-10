

import os
from fastapi import FastAPI, Request, Response, HTTPException
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
from dotenv import load_dotenv

# Import our AI logic
from ai_core import get_ai_response

load_dotenv()
app = FastAPI()

# Configuration (same as before)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
MY_PHONE_NUMBER = os.getenv("MY_PHONE_NUMBER")
BASE_URL = os.getenv("BASE_URL")

if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, MY_PHONE_NUMBER, BASE_URL]):
    raise RuntimeError("One or more required environment variables are missing. Please check your .env file.")

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
conversations = {}

@app.get("/make-call")
def make_outbound_call():
    try:
        print(f"Initiating call from {TWILIO_PHONE_NUMBER} to {MY_PHONE_NUMBER}...")
        
        twiML_url = f"{BASE_URL}/voice/incoming"

        call = twilio_client.calls.create(
            to=MY_PHONE_NUMBER,
            from_=TWILIO_PHONE_NUMBER,
            url=twiML_url
        )
        
        print(f"Call initiated successfully. SID: {call.sid}")
        return {"status": "Call initiated", "sid": call.sid}
    
    except Exception as e:
        print(f"Error initiating call: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/voice/incoming", response_class=Response)
async def incoming_call(request: Request):
    print("Call connected. Generating initial TwiML response.")
    twiml = VoiceResponse()
    
    form_data = await request.form()
    call_sid = form_data.get('CallSid')
    
    if call_sid not in conversations:
        conversations[call_sid] = []
        print(f"New conversation started for CallSid: {call_sid}")

    # Updated to use Hindi voice and language
    gather = Gather(
        input='speech', 
        action='/voice/handle-speech', 
        speechTimeout='auto',
        language='hi-IN'  # Hindi language for speech recognition
    )
    
    # Hindi greeting message
    gather.say(
        "नमस्ते, आपका स्वागत है आज मैं आपकी कैसे सहायता कर सकती हूं?", 
        voice='Polly.Aditi',  # Hindi voice
        language='hi-IN'
    )
    twiml.append(gather)

    twiml.redirect('/voice/incoming', method='POST')
    return Response(content=str(twiml), media_type="application/xml")

@app.post("/voice/handle-speech", response_class=Response)
async def handle_speech(request: Request):
    twiml = VoiceResponse()
    
    form_data = await request.form()
    call_sid = form_data.get('CallSid')
    user_speech = form_data.get('SpeechResult')
    
    print(f"[{call_sid}] User said: '{user_speech}'")
    
    if call_sid not in conversations:
        print(f"Warning: Received speech from an unknown CallSid: {call_sid}")
        twiml.say(
            "मुझे खुशी है, हमारे सत्र में कोई समस्या थी। कृपया वापस कॉल करें।", 
            voice='Polly.Aditi',
            language='hi-IN'
        )
        twiml.hangup()
        return Response(content=str(twiml), media_type="application/xml")

    if user_speech:
        history = conversations[call_sid]
        ai_text_response = await get_ai_response(user_speech, history)
        conversations[call_sid] = history
        
        gather = Gather(
            input='speech', 
            action='/voice/handle-speech', 
            speechTimeout='auto',
            language='hi-IN'  # Hindi language for speech recognition
        )
        
        # AI response in Hindi
        gather.say(
            ai_text_response, 
            voice='Polly.Aditi',  # Hindi voice
            language='hi-IN'
        )
        twiml.append(gather)
        
    else:
        # Hindi fallback message
        twiml.say(
            "मुझे कुछ सुनाई नहीं दिया। कृपया दोहराएं।", 
            voice='Polly.Aditi',
            language='hi-IN'
        )
        gather = Gather(
            input='speech', 
            action='/voice/handle-speech', 
            speechTimeout='auto',
            language='hi-IN'
        )
        twiml.append(gather)

    twiml.redirect('/voice/handle-speech', method='POST')  # Continue conversation instead of hanging up
    return Response(content=str(twiml), media_type="application/xml")