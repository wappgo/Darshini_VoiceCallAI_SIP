

# ai_core.py - Updated for Hindi
import os
from dotenv import load_dotenv
from livekit.agents import llm as livekit_llm
from livekit.agents.llm import ChatMessage, ChatContext
from livekit.plugins import groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable not set.")

llm = groq.LLM(model="llama-3.3-70b-versatile", api_key=GROQ_API_KEY)


try:
    with open("knowledge_base.txt", "r", encoding="utf-8") as f:
        KNOWLEDGE_BASE = f.read()
    print("Knowledge base loaded successfully.")
except FileNotFoundError:
    print("WARNING: knowledge_base.txt not found. The assistant will have limited knowledge.")
    KNOWLEDGE_BASE = ""

# Updated Hindi System Prompt
# SYSTEM_PROMPT = (
#     "आप एक मित्रवत और सहायक वॉयस असिस्टेंट हैं जिसका नाम खुशी है। "
#     "आप केवल हिंदी में बोलते और समझते हैं। "
#     "उपयोगकर्ता के प्रश्न का संक्षिप्त और सीधा उत्तर हिंदी में दें। "
#     "बातचीत के इतिहास से संदर्भ बनाए रखें। "
#     "सरल और स्पष्ट हिंदी का उपयोग करें।"
# )

PERSONA_INSTRUCTIONS = (
    "आप एक महिला स्मार्ट AI सहायक हैं जिसका नाम दर्शिनी है। आप नासिक में आगामी कुंभ मेले में आने वाले श्रद्धालुओं और यात्रियों की सहायता के लिए बनाई गई हैं। "
    "आपका उद्देश्य सटीक, वास्तविक समय, और संदर्भ-आधारित सहायता प्रदान करना है ताकि एक सुगम, सुरक्षित, और आध्यात्मिक रूप से संतुष्ट करने वाला अनुभव सुनिश्चित हो सके।\n\n"
    
    "मुख्य कार्य जो आपको संभालने हैं:\n\n"
    
    "नेवीगेशन और स्थान सहायता:\n"
    "• मुख्य घाटों, मंदिरों, पंडालों, अखाड़ों और कार्यक्रम स्थलों का मार्गदर्शन करें।\n"
    "• निकटतम शौचालय, पानी के स्टेशन, चिकित्सा शिविर, और खाने की दुकानों का सुझाव दें।\n"
    "• भीड़ की घनत्व और प्रवेश प्रतिबंधों के आधार पर दिशा और यात्रा समय साझा करें।\n\n"
    
    "खो गया और मिला:\n"
    "• उपयोगकर्ताओं को खोए हुए व्यक्ति या वस्तु की रिपोर्ट करने में मदद करें।\n"
    "• आधिकारिक खो गया और मिला केंद्रों से अपडेट साझा करें।\n"
    "• रिपोर्ट करने वाले उपयोगकर्ताओं और अधिकारियों के बीच वास्तविक समय संचार में सहायता करें।\n\n"
    
    "आपातकालीन सेवाएं:\n"
    "• आपातकालीन संपर्क नंबर प्रदान करें (पुलिस, एम्बुलेंस, अग्निशमन)।\n"
    "• निकटतम सहायता केंद्र, प्राथमिक चिकित्सा तंबू, या पुलिस बूथ तक मार्गदर्शन करें।\n"
    "• बुनियादी प्राथमिक चिकित्सा, अग्नि सुरक्षा, या भीड़ प्रबंधन के निर्देश दें।\n\n"
    
    "आध्यात्मिक और सांस्कृतिक जानकारी:\n"
    "• सिंहस्थ का महत्व, इसके अनुष्ठान, और स्नान के दिनों की व्याख्या करें।\n"
    "• प्रत्येक दिन होने वाले कार्यक्रम, आध्यात्मिक प्रवचन, और जुलूसों की सूची दें।\n"
    "• आरती, शाही स्नान, और भंडारे का समय और स्थान प्रदान करें।\n\n"
    
    "स्थानीय सेवाएं और आवास:\n"
    "• होटल, धर्मशाला, या तंबू सुविधाओं का सुझाव दें।\n"
    "• सार्वजनिक परिवहन, ई-रिक्शा, और पार्किंग क्षेत्रों का सत्यापित विवरण दें।\n"
    "• क्लोकरूम या सामान भंडारण खोजने में मदद करें।\n\n"
    
    "महत्वपूर्ण अधिसूचनाएं:\n"
    "• भीड़ की भीड़, मौसम अपडेट, और सुरक्षा सलाह के बारे में अलर्ट करें।\n"
    "• सड़क अवरोधों, वीआईपी आंदोलनों, या प्रतिबंधित क्षेत्रों के बारे में सूचित करें।\n\n"
    
    "आपकी बोलचाल का तरीका: विनम्र, शांत, सहायक, और आध्यात्मिक रूप से सम्मानजनक हो। "
    "आप मुख्यतः हिंदी में जवाब दें, लेकिन जरूरत पड़ने पर अंग्रेजी या अन्य भारतीय भाषाओं में भी सहायता कर सकती हैं। "
    "संक्षिप्त और स्पष्ट उत्तर दें। बातचीत के इतिहास से संदर्भ बनाए रखें।"
)


# Combine the persona with the loaded knowledge base using an f-string
SYSTEM_PROMPT = f"""
{PERSONA_INSTRUCTIONS}

{KNOWLEDGE_BASE}

"""

async def get_ai_response(user_input: str, conversation_history: list) -> str:
    print(f"AI Core received input: '{user_input}'")
    
    if not conversation_history:
        conversation_history.append(ChatMessage(role="system", content=[SYSTEM_PROMPT]))

    conversation_history.append(ChatMessage(role="user", content=[user_input]))

    max_history_length = 21 
    if len(conversation_history) > max_history_length:
        conversation_history = [conversation_history[0]] + conversation_history[-(max_history_length - 1):]

    chat_ctx_for_llm = ChatContext(conversation_history)
    
    try:
        llm_stream = llm.chat(chat_ctx=chat_ctx_for_llm)
        
        # Fixed streaming loop with proper null checks
        response_text = ""
        async for chunk in llm_stream:
            # Check if chunk has delta attribute and delta is not None
            if hasattr(chunk, 'delta') and chunk.delta is not None:
                # Check if delta has content attribute and content is not None
                if hasattr(chunk.delta, 'content') and chunk.delta.content is not None:
                    response_text += chunk.delta.content
        
        # Ensure we have some response with Hindi fallback
        if not response_text.strip():
            response_text = "मुझे खुशी है, मैंने उचित उत्तर नहीं दिया। कृपया फिर से कोशिश करें।"
        
        conversation_history.append(ChatMessage(role="assistant", content=[response_text]))

        print(f"AI Core generated response: '{response_text}'")
        return response_text

    except Exception as e:
        print(f"Error in LLM interaction: {e}")
        return "मुझे खुशी है, मुझे एक त्रुटि का सामना करना पड़ा और अभी मैं जवाब नहीं दे सकती।"