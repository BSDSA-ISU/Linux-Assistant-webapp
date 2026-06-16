import glob
from pathlib import Path
import shlex
import shutil
import subprocess
from ddgs import DDGS
import json

def config_loader():
    with open('./config/configs.json', 'r') as file:
        config = json.load(file)

        return config

def cmd(command: str) -> list[dict]:
    """
    Runs a command on linux like timedatectl, uptime, date etc.
    """

    # 1. Block shell chaining and redirection symbols entirely
    # DANGEROUS_SYMBOLS = [";", "&&", "||", "|", "`", "$", ">", "<"]
    DANGEROUS_SYMBOLS = ["&&", "||", "`", ">", "<"]
    if any(symbol in command for symbol in DANGEROUS_SYMBOLS):
        return [{"error": "Execution denied: Shell chaining or redirection symbols are forbidden."}]

    # 2. Parse the command safely to isolate the primary executable
    try:
        parsed_command = shlex.split(command)
        if not parsed_command:
            return [{"error": "Empty command."}]
        base_binary = parsed_command[0].lower()
    except Exception:
        return [{"error": "Invalid command formatting."}]

    # 3. Comprehensive Blacklist of forbidden binaries
    FORBIDDEN_BINARIES = {
        # File destruction / modification
        "rm", "shred", "dd", "chmod", "chown", "mkfs", "fdisk", "parted",
        # Shell spawning / Escaping
        "sh", "bash", "zsh", "csh", "tcsh", "tmux", "screen", "python", "perl",
        # Privilege escalation
        "sudo", "su", "passwd", "chsh",
        # Network / Exfiltration hazards
        "curl", "wget", "nc", "netcat", "nmap", "ssh", "ftp", "scp", "rsync",
        # Package managers (to prevent unwanted installs/removals)
        "pacman", "yay", "paru", "apt", "dnf", "pip",
        # Text editors (which hang the terminal waiting for user input)
        "nano", "vim", "vi", "emacs", "neovim"
    }

    if base_binary in FORBIDDEN_BINARIES:
        return [{"error": f"Execution denied: '{base_binary}' is a forbidden command."}]

    # NEW: Safely expand wildcards (globs) if present in the arguments
    final_args = [parsed_command[0]]
    for arg in parsed_command[1:]:
        if "*" in arg or "?" in arg:
            expanded = glob.glob(arg)
            if expanded:
                final_args.extend(expanded)
            else:
                # If no files match the wildcard, pass it literally so the binary fails naturally
                final_args.append(arg)
        else:
            final_args.append(arg)

    print("Gemini is running:", " ".join(final_args))
    
    try:
        result = subprocess.run(
            final_args,  # Pass the expanded arguments list here
            capture_output=True,
            text=True,
            timeout=5
        )
        
        output = result.stdout if result.stdout else result.stderr
        
        return [
            {"command": command, "output": line}
            for line in output.splitlines()
        ]
    except subprocess.TimeoutExpired:
        return [{"error": "Command timed out."}]
    except Exception as e:
        return [{"error": f"Execution failed: {str(e)}"}]

def web_news_search(query: str) -> list[dict]:
    """
    Searches the live web specifically for recent news articles, breaking updates, 
    and press releases. Use this if the user asks for 'news', 'latest events', or 'recent updates'.
    """

    # Format it cleanly so Gemini gets a uniform list of results
    formatted_results = []

    print("Gemini is searching NEWS:", query)
    try:
        # DDGS().news returns results with 'title', 'url', 'body', 'date', and 'source'
        results = DDGS().news(query, max_results=10)
        
        for r in results:
            formatted_results.append({
                "title": r.get("title"),
                "href": r.get("url"), # Renamed url to href to keep it consistent for your UI links
                "body": r.get("body")
            })
        return formatted_results
    except Exception as e:
        print(f"News search failed: {e}")
        return []


def web_search(query: str) -> list[dict]:
    """
    Searches the live web for general information, guides, and articles. 
    Returns a list of dictionaries with title, href, and body.
    """
        
    print("Gemini is searching text:", query)
    try:
        return DDGS().text(query, max_results=22)
    except Exception as e:
        print(f"Text search failed: {e}")
        return []

def image_search(query: str) -> list[dict]:
    """
    Searches the web for pictures and send to user as markdown.
    """

    print("Gemini is searching Images:", query)
    try:
        return DDGS().images(query, max_results=15)
    except Exception as e:
        print(f"Text search failed: {e}")
        return []

def clean_session():
    try:
        sessions = Path("./flask_session/")
        for item in sessions.iterdir():
            if item.is_dir():
                shutil.rmtree(item)  # Removes subdirectories and their contents
                print("Session Cleaned")
            else:
                item.unlink()        # Removes individual files
    except:
        print("No jobs, already cleaned")