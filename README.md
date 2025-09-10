# AI Voice Assistant for Ujjain Kumbh Mela (Project Darshini)

## Overview

**Project Darshini** is a sophisticated, AI-powered voice assistant designed to provide real-time information and support to pilgrims and tourists attending the Ujjain Kumbh Mela. Users can call a designated phone number and have a natural, voice-based conversation in Hindi with an AI assistant that is equipped with a specific knowledge base about the event.

The assistant, named **Darshini**, can answer questions about key dates, event schedules, navigation to important locations (ghats, temples, ashrams), emergency services, accommodation, and transportation, ensuring a safer and more organized experience for everyone.

This project demonstrates a powerful integration of modern technologies:
- **Twilio** for telephony and voice communication.
- **FastAPI** for a robust and scalable web server.
- **Groq** for ultra-low-latency Large Language Model (LLM) inference.
- **LiveKit's Python libraries** for standardized interaction with the LLM.

## Features

- **Natural Language Conversation:** Users can speak naturally in Hindi to ask questions.
- **Knowledge Base Integration:** The AI's responses are grounded in a curated, up-to-date knowledge base, ensuring accuracy.
- **Outbound Calling for Testing:** Includes a simple endpoint to trigger a call *from* the assistant *to* your phone for easy development and testing.
- **Multilingual Support:** Built with a Hindi-first approach but can be easily adapted to other languages.
- **Specific Persona:** The AI assistant has a well-defined persona ("Darshini") tailored to be a helpful, calm, and respectful guide for a spiritual event.
- **Key Information Areas:**
    - Event Dates & Schedules (e.g., Shahi Snan)
    - Location & Navigation (e.g., "How do I get to Ramkund?")
    - Emergency & Support Helplines
    - Accommodation & Transport Details
    - Cultural Information (e.g., Aarti timings)

## System Architecture

The application operates on a stateless, webhook-based model orchestrated by Twilio:

1.  **Call Initiation:** A call is made from a Twilio number to the user's phone (triggered by a web endpoint for testing).
2.  **Twilio Webhook:** When the user answers, Twilio makes an HTTP POST request to our FastAPI server's `/voice/incoming` endpoint.
3.  **TwiML Response (Listen):** The server responds with TwiML (Twilio Markup Language) instructions. Initially, this TwiML tells Twilio to play a greeting message and then listen for the user's speech (`<Gather>`).
4.  **Speech-to-Text (STT):** Twilio captures the user's voice, converts it to text using its Hindi STT engine, and makes another POST request to the `/voice/handle-speech` endpoint with the transcribed text.
5.  **AI Core Logic:**
    - The server receives the text.
    - It retrieves the conversation history.
    - It sends the history, the new user input, and the entire **Kumbh Mela knowledge base** to the Groq Llama 3 LLM.
6.  **TwiML Response (Speak):**
    - The LLM generates a text response in Hindi.
    - The server places this text into a new TwiML response using the `<Say>` verb with a Hindi voice (`Polly.Aditi`).
    - This response also includes another `<Gather>` instruction, creating a continuous conversational loop.
7.  **Loop or Hangup:** The cycle repeats until the user hangs up.

## Tech Stack

- **Backend:** Python 3.10+
- **Web Framework:** FastAPI
- **Telephony & Voice:** Twilio API, TwiML
- **LLM Provider:** Groq (via `livekit-plugins-groq`)
- **Core Libraries:** `twilio`, `fastapi`, `uvicorn`, `python-dotenv`, `livekit-agents`

## Setup and Installation

### Prerequisites

- A Twilio account with a phone number.
- A GroqCloud account and API key.
- Python 3.10 or higher.
- `ngrok` for exposing your local server to the internet during development.

### 1. Clone the Repository

# Twilio + LiveKit AI Assistant Setup

```bash
# 1. Clone the Repository
git clone <your-repository-url>
cd <your-repository-directory>

# 2. Create a Virtual Environment
python -m venv venv
# Activate the virtual environment
# On macOS / Linux:
source venv/bin/activate
# On Windows:
# .\venv\Scripts\activate

# 3. Install Dependencies
# Create a requirements.txt file with the following content:
echo "fastapi
uvicorn[standard]
python-dotenv
twilio
livekit-agents
livekit-plugins-groq
python-multipart" > requirements.txt

# Install all dependencies
pip install -r requirements.txt

# 4. Configure Environment Variables
# Create a .env file in the root directory:
echo "# Groq API Key
GROQ_API_KEY=\"your_groq_api_key_here\"

# Twilio Credentials
TWILIO_ACCOUNT_SID=\"ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\"
TWILIO_AUTH_TOKEN=\"your_auth_token_from_twilio\"

# Your Phone Numbers
TWILIO_PHONE_NUMBER=\"+15551234567\"
MY_PHONE_NUMBER=\"+919876543210\"

# This will be your public ngrok URL
BASE_URL=\"https://something.ngrok-free.app\"" > .env

# 5. Update the Knowledge Base
# Edit knowledge_base.txt to add information for the AI assistant.

# 6. Running the Application

# Step 6a: Start ngrok to expose local port 8000
ngrok http 8000
# Copy the HTTPS URL from ngrok and update BASE_URL in .env

# Step 6b: Start the FastAPI Server
uvicorn twilio_app:app --host 0.0.0.0 --port 8000

# Step 6c: Trigger a Test Call
# Open your browser:
http://localhost:8000/make-call
# Answer the call and start your conversation with the AI assistant in Hindi!
