# Browser Automation with Flask and Playwright

This project is a Flask-based web application that integrates browser automation using Playwright and Gemini LLM. It allows users to execute tasks via prompts and update the Gemini API key dynamically.

## Features

- **Browser Automation**: Perform web tasks such as navigating to a URL, removing ads, scrolling, and capturing headlines.
- **Dynamic Prompt Execution**: Users can input prompts to define tasks for the agent.
- **Gemini API Key Management**: Update the Gemini API key directly from the web interface.
- **Live Output Streaming**: View real-time terminal output of the agent's execution.
- **Headless Mode**: Option to run the browser in headless mode.

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd browser_use_flask_playwright
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   playwright install
   ```

3. Set up the `.env` file:
   ```bash
   echo "GOOGLE_API_KEY=<your-gemini-api-key>" > .env
   ```

4. Run the Flask application:
   ```bash
   python app.py
   ```

## Usage

1. Open the web interface at `http://127.0.0.1:5000`.
2. Enter a prompt to define the task for the agent (e.g., "start browser on https://example.com\nremove any ads\nscroll if needed, capture 3 headlines only\nprint the headlines found").
3. Optionally, enable headless mode.
4. Submit the prompt and view the live output.
5. Update the Gemini API key using the provided form.

## Example Prompt

```
start browser on https://infobae.com
remove any ads that appear if they appear
scroll if needed, capture 3 headlines only
print the headlines found
```

## File Structure

- `app.py`: Flask backend handling agent execution and API key updates.
- `templates/index.html`: Frontend for user interaction.
- `.env`: Environment variables file for storing the Gemini API key.
- `requirements.txt`: List of dependencies.
- `.gitignore`: Excludes unnecessary files from version control.

## Notes

- Ensure the Gemini API key is valid and has sufficient quota.
- This application is intended for development purposes. Use a production WSGI server for deployment.

## License

This project is licensed under the MIT License.
