# app.py - Main Flask application file

from flask import Flask, render_template, request
from google import genai
from google.genai.types import Content
import json
import os

# ******
# ** YAHAN API KEY DALO **
# Kripya 'YOUR_GEMINI_API_KEY_HERE' ki jagah apni asli API Key daalein
API_KEY = 'AIzaSyDHB1pt2CE-J9VFok63dQU-3T5CgHVdPS8' 
# ******

app = Flask(__name__)

# Gemini Client ka setup
client = None
try:
    if not API_KEY or API_KEY == 'YOUR_GEMINI_API_KEY_HERE':
        raise ValueError("Kripya API_KEY ko app.py mein daalein.")
    
    client = genai.Client(api_key=API_KEY)
    print("AI Assistant (Flask) is ready. (Check http://127.0.0.1:5000)")
except Exception as e:
    print(f"\n🚨 GADBAD! CONNECTION FAIL. 🚨\nError: {e}")
    client = None

# Main route jo GET aur POST requests ko handle karta hai
@app.route("/", methods=['GET', 'POST'])
def home():
    
    # Connection error check
    if client is None:
        # Agar connection nahi hua toh simple error message render karein
        return "<h1>Configuration Error</h1><p>Gemini API key ya Internet mein gadbad hai. Kripya Terminal check karein.</p>", 500

    user_input = None
    assistant_response = ""
    history_dicts = []
    
    # Check karein agar yeh POST request hai (jab user ne form submit kiya ho)
    if request.method == 'POST':
        user_input = request.form.get('user_input')
        chat_history_data = request.form.get('chat_history_data')
        
        # 1. Chat History Load karna
        history_json = chat_history_data if chat_history_data else "[]"
        
        try:
            history_dicts = json.loads(history_json)
            # Content objects banana
            history_data = [Content.from_dict(h) for h in history_dicts]
        except Exception:
            history_data = []

        
        if user_input:
            try:
                # Naya chat session purani history ke saath banao
                temp_chat = client.chats.create(model='gemini-2.5-flash', history=history_data)
            except Exception:
                assistant_response = "Maaf karna, chat shuru karne mein gadbad hui."

            # --- FEATURE LOGIC (Score/Pic/Chat) ---
            
            # A. LIVE SCORE CHECK
            if any(keyword in user_input.lower() for keyword in ["score", "cricket", "livescore", "kitna bana"]):
                
                score_search_reply = temp_chat.send_message(
                    f"User ne kaha hai: '{user_input}'. Tum is sawal ka jawab dene ke liye ek perfect Google search query (sawaal) banao, jisse user ko turant live score mil jaaye. Jawab sirf ek line ka hona chahiye jismein woh search query ho."
                )
                search_query = score_search_reply.text.strip()
                google_link = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
                
                assistant_response = (
                    "Main khud real-time score nahi dekh sakta, lekin main aapko turant score dhoondhne mein madad karta hoon. "
                    "Aap niche diye gaye link par turant click karke score dekh sakte hain:<br><br>"
                    f"<a href='{google_link}' target='_blank' style='background-color:#4CAF50; color:white; padding:8px 15px; text-decoration:none; border-radius:5px; font-weight:bold;'>🏏 Turant Live Score Dekhein 🏏</a>"
                )

            # B. PIC CHECK
            elif any(keyword in user_input.lower() for keyword in ["pic banao", "tasveer banao", "image banao"]):
                
                smart_reply = temp_chat.send_message(
                    f"User ne kaha hai: '{user_input}'. Tum is sawal ka jawab dene ke liye ek perfect, high-quality image prompt banao jise user Microsoft Copilot jaise free tool mein use kar sake. Jawab mein pehli line sirf woh prompt honi chahiye."
                )
                
                prompt_text = smart_reply.text.split('\n')[0]
                
                assistant_response = (
                    "Main aapke liye tasveer nahi bana sakta, lekin main aapko free AI tool ke liye perfect prompt bana sakta hoon.<br><br>"
                    "Aap is Prompt ko Microsoft Copilot mein paste karein:<br>"
                    f"👉 <span style='color: #4A90E2;'>{prompt_text}</span><br><br>"
                    "Iske baad aapko apni tasveer mil jaayegi!"
                )
                
            # C. NORMAL CHAT
            else:
                try:
                    gemini_response = temp_chat.send_message(user_input)
                    assistant_response = gemini_response.text
                except Exception:
                    assistant_response = "Maaf karna, baat-cheet mein koi gadbad ho gayi. API key check karein."
            
            # 3. Chat History update karna
            # Flask mein history ko render karne ke liye taiyar karna
            history_dicts = [h.model_dump() for h in temp_chat.get_history()]

    # 4. HTML file ko render karna
    # Flask mein render_template use karein
    return render_template(
        "index.html",
        user_input=user_input,
        ai_response=assistant_response,
        history=history_dicts
    )

if __name__ == "__main__":
    app.run(debug=True)