# Linux Assistant

A web-based AI assistant interface for Linux systems, designed to bridge the gap between natural language interaction and system management.

![Minoriko](https://media1.tenor.com/m/kfCcMd9vCSgAAAAC/aki-minoriko-touhou.gif)

## Features

- **Natural Language Interaction:** Chat with your system using the Google Gemini API.
- **System Commands:** Execute non-destructive system commands directly from the interface.
- **Web Search:** Perform web searches using DuckDuckGo (via `ddgs`).
- **News Aggregation:** Fetch the latest news from the web.

## Tech Stack

- **Backend:** Python (Flask)
- **Frontend:** HTML/CSS/JavaScript
- **AI/APIs:** Google Gemini, DuckDuckGo Search
- **Tooling:** `uv` (package management)

## Getting Started

*(Note: Please update this section to reflect your specific deployment/development workflow)*

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd linux-assistant-webapp
   ```

2. **Setup Environment:**
   Ensure you have `uv` installed.
   ```bash
   uv sync
   ```

3. **Configure:**
   Ensure your environment variables (like `GEMINI_API_KEY`) are set. Refer to `config/configs.json` for structure.

4. **Run:**
   ```bash
   uv run python main.py
   ```

## Contributors

<a href="https://github.com/BSDSA-ISU/Linux-Assistant/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=BSDSA-ISU/Linux-Assistant" />
</a>

*Made with [contrib.rocks](https://contrib.rocks).*

---

## License

[MIT](./LICENSE)

---

*Thank you and peace out!*

![Minoriko and Shizuha](https://media1.tenor.com/m/cH8iW9HL_O8AAAAC/minoriko-aki-shizuha-aki.gif)
