from datetime import datetime
import os
from flask import Flask, render_template, request, jsonify, session
from google import genai
from google.genai import types
from dotenv import load_dotenv
from flask_session import Session
import shlex
from goodies.tools import config_loader, open_site_or_file, video_search, web_news_search, clean_session, web_search, image_search, cmd

config = config_loader()

# for config
TOOL_MAPPING = {
    "web_search": web_search,
    "web_news_search": web_news_search,
    "cmd": cmd,
    "image_search": image_search,
    "open_site_or_file": open_site_or_file,
    "video_search": video_search
}

# Applies the configuration tool
# This looks at each string in config['tools'] and fetches the corresponding variable
active_tools = []

for tool_name in config["tools"]:
    if tool_name in TOOL_MAPPING:
        
        actual_tool_object = TOOL_MAPPING[tool_name]
        active_tools.append(actual_tool_object)

print("Using:", active_tools)
print('Available tools are: ["web_search", "web_news_search", "video_search", "cmd", "image_search"]')

clean_session()

CURRENTTIME = datetime.now()

load_dotenv()

app = Flask(__name__)
# Secret key needed to securely sign Flask client-side sessions
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "super-secret-dev-key")

# The SDK automatically targets GEMINI_API_KEY from environment variables
client = genai.Client()


# --- SERVER-SIDE SESSION CONFIGURATION ---
app.config["SESSION_TYPE"] = "filesystem"  # Saves session data as local files
app.config["SESSION_PERMANENT"] = False     # Session expires when browser closes
Session(app)                               # <--- Initialize the extension
# ----------------------------------------

# Using the performant gemini-3.5-flash as the base driver 3.1 flash lite for attitude
# MODEL_ID = "gemma-4-26b-a4b-it"
MODEL_ID = "gemini-3.1-flash-lite-preview"

@app.route('/')
def index():
    chat_history = session.get('chat_history', [])
    return render_template('index.html', chat_history=chat_history)

# Add standard color codes to make your terminal scannable at a glance
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    user_message = data.get('message', '').strip()

    if not user_message:
        return jsonify({'error': 'Message content cannot be empty.'}), 400

    if 'chat_history' not in session:
        session['chat_history'] = []

    try:
        with open("./instructions/gemini-chan.txt", "r", encoding="utf-8") as e:
            linux_instructions = e.read()

        chat_session = client.chats.create(
            model=MODEL_ID,
            history=session['chat_history'],
            config=types.GenerateContentConfig(
                system_instruction=linux_instructions,
                tools=active_tools,
            )
        )

        # Fire request
        response = chat_session.send_message(user_message)
        
        # --- TERMINAL DEBUGGER ---
        meta = response.usage_metadata
        if meta and config["debugging_mode"]:
            p_tokens = getattr(meta, 'prompt_token_count', 0)
            c_tokens = getattr(meta, 'candidates_token_count', 0)
            t_tokens = getattr(meta, 'total_token_count', 0)
            
            print(f"\n⚡ {CYAN}[Gemini Token Debugger]{RESET}")
            print(f"├─ Input (Prompt + History + Tools): {YELLOW}{p_tokens}{RESET}")
            print(f"├─ Output (Generation):              {GREEN}{c_tokens}{RESET}")
            print(f"└─ Total Context Window Used:        {CYAN}{t_tokens} / 1,048,576{RESET}\n")
        # -------------------------

        # Serialize history back to storage
        updated_history = []
        for content in chat_session.get_history():
            parts_list = [{'text': part.text} for part in content.parts if part.text]  # pyright: ignore[reportOptionalIterable]
            updated_history.append({
                'role': content.role,
                'parts': parts_list
            })
            
        session['chat_history'] = updated_history
        
        # Return only the text to the frontend frontend (no debug payload leak)
        print(response.text)
        return jsonify({'response': response.text})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/sw.js')
def serve_sw():
    return app.send_static_file('sw.js') # If sw.js is sitting inside /static/

@app.route('/api/clear', methods=['POST'])
def clear():
    session.pop('chat_history', None)
    return jsonify({'status': 'cleared'})

if __name__ == '__main__':
    app.run(debug=True)
