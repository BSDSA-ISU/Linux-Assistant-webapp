import os
from datetime import datetime
from flask import Flask, jsonify, render_template, request, session
from flask_session import Session
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Import custom tools and configurations
from goodies.tools import (
    cmd,
    config_loader,
    image_search,
    open_site_or_file,
    web_news_search,
    web_search,
    video_search,
    clean_session,
)

# Initialize application and load configuration
load_dotenv()
config = config_loader()

# Initialize Home path
home_dir = os.path.expanduser("~")

# Mapping for dynamic tool loading
TOOL_MAPPING = {
    "web_search": web_search,
    "web_news_search": web_news_search,
    "cmd": cmd,
    "image_search": image_search,
    "open_site_or_file": open_site_or_file,
    "video_search": video_search
}

# Load active tools based on config
active_tools = [TOOL_MAPPING[t] for t in config.get("tools", []) if t in TOOL_MAPPING]
print(f"Using tools: {[t.__name__ for t in active_tools]}")

# Pre-session cleanup and initialization
clean_session()
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "super-secret-dev-key")

# Server-side session configuration
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
Session(app)

# Initialize Gemini Client
client = genai.Client()
MODEL_ID = config.get("model", "gemini-2.0-flash")

# Terminal UI constants
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"

def log_token_usage(meta):
    """Logs token usage statistics to the terminal."""
    if not meta or not config.get("debugging_mode"):
        return
        
    p_tokens = getattr(meta, 'prompt_token_count', 0)
    c_tokens = getattr(meta, 'candidates_token_count', 0)
    t_tokens = getattr(meta, 'total_token_count', 0)
    
    print(f"\n⚡ {CYAN}[Gemini Token Debugger]{RESET}")
    print(f"├─ Input:  {YELLOW}{p_tokens}{RESET}")
    print(f"├─ Output: {GREEN}{c_tokens}{RESET}")
    print(f"└─ Total:  {CYAN}{t_tokens} / 1,048,576{RESET}\n")

@app.route('/')
def index():
    """Renders the chat interface."""
    chat_history = session.get('chat_history', [])
    return render_template('index.html', chat_history=chat_history)

@app.route('/api/chat', methods=['POST'])
def chat():
    """Processes incoming chat messages."""
    data = request.get_json() or {}
    user_message = data.get('message', '').strip()

    if not user_message:
        return jsonify({'error': 'Message content cannot be empty.'}), 400

    if 'chat_history' not in session:
        session['chat_history'] = []

    try:
        # Load system instructions
        with open(config["instruction"], "r", encoding="utf-8") as f:
            system_instruction_content = f.read()
            visible_files = os.listdir(home_dir)
            # Filter out hidden files (.) to save tokens
            dir_snapshot = [f for f in visible_files if not f.startswith('.')]
            fs_context = f"\n\nUser's current local home directory is: {home_dir}\nContents: {', '.join(dir_snapshot)}"    

        full_instruction = system_instruction_content + fs_context

        chat_session = client.chats.create(
            model=MODEL_ID,
            history=session['chat_history'],
            config=types.GenerateContentConfig(
                temperature=1.2,
                system_instruction=full_instruction,
                tools=active_tools,
            )
        )

        response = chat_session.send_message(user_message)
        
        # Debugging output
        log_token_usage(response.usage_metadata)

        # Update session history
        updated_history = []
        for content in chat_session.get_history():
            parts = [{'text': part.text} for part in content.parts if part.text]
            updated_history.append({'role': content.role, 'parts': parts})
            
        session['chat_history'] = updated_history
        
        print(response.text)
        return jsonify({'response': response.text})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/sw.js')
def serve_sw():
    """Serves service worker script."""
    return app.send_static_file('sw.js')

@app.route('/api/clear', methods=['POST'])
def clear():
    """Clears the chat history session."""
    session.pop('chat_history', None)
    return jsonify({'status': 'cleared'})

if __name__ == '__main__':
    app.run(debug=True)
