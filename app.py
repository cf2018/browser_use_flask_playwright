from flask import Flask, render_template, request, jsonify
import asyncio
import threading
import os
from dotenv import load_dotenv
from browser_use import Agent, Browser, BrowserConfig
from browser_use.llm import ChatGoogle, UserMessage
import sys
import io
import logging

load_dotenv()

app = Flask(__name__)

# Store terminal output for live updates
terminal_output = []

def run_agent_task(task, headless, output_callback):
    class StreamCatcher(io.StringIO):
        def write(self, msg):
            output_callback(msg)
            super().write(msg)
            self.flush()
        def flush(self):
            pass
    old_stdout, old_stderr = sys.stdout, sys.stderr
    sys.stdout = sys.stderr = StreamCatcher()
    # Set up logging to also go to StreamCatcher
    handler = logging.StreamHandler(sys.stdout)
    logging.getLogger().addHandler(handler)
    os.environ["PYTHONUNBUFFERED"] = "1"
    try:
        async def agent_runner():
            google_api_key = os.getenv("GOOGLE_API_KEY")
            llm = ChatGoogle(model='gemini-2.0-flash-exp')
            browser_config = BrowserConfig(
                browser_type='chromium',
                headless=headless,
            )
            browser = Browser(config=browser_config)
            agent = Agent(
                task=task,
                llm=llm,
                browser=browser,
            )
            logging.info(f"Agent initialized with task: {task}")
            print("Starting agent...\n")

            # Extract target URL from the prompt
            target_url = task.split("start browser on ")[1].split("\n")[0].strip()
            logging.info(f"Navigating to: {target_url}")
            await browser.navigate(target_url)

            # Execute the prompt directly
            history = await agent.run()

            # Debugging navigation state
            current_page = await browser.get_current_page()
            current_url = current_page.url if current_page else "Unknown"
            logging.info(f"Current browser URL: {current_url}")

            # Print the final result
            print("\n--- FINAL RESULT ---\n")
            print(str(history.final_result()) + "\n")

            await browser.close()
            logging.info("Browser closed.")
            output_callback("__AGENT_DONE__")
        asyncio.run(agent_runner())
    finally:
        logging.getLogger().removeHandler(handler)
        sys.stdout, sys.stderr = old_stdout, old_stderr

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route("/run", methods=["POST"])
def run():
    prompt = request.form.get("prompt")
    headless = request.form.get("headless") == "on"
    logging.info(f"Received prompt: {prompt}")
    logging.info(f"Headless mode: {headless}")
    terminal_output.clear()
    def output_callback(msg):
        terminal_output.append(msg)
    thread = threading.Thread(target=run_agent_task, args=(prompt, headless, output_callback))
    thread.start()
    return jsonify({"status": "started"})

@app.route("/output")
def output():
    done = any("__AGENT_DONE__" in msg for msg in terminal_output)
    # Show all output except the completion signal
    output_text = "".join([
        msg for msg in terminal_output
        if "__AGENT_DONE__" not in msg
    ])
    return jsonify({"output": output_text, "done": done})

@app.route("/update_api_key", methods=["POST"])
def update_api_key():
    new_api_key = request.form.get("api_key")
    if new_api_key:
        with open(".env", "w") as env_file:
            env_file.write(f"GOOGLE_API_KEY={new_api_key}\n")
        load_dotenv()  # Reload the environment variables
        logging.info("Gemini API key updated successfully.")
        return jsonify({"status": "success", "message": "API key updated."})
    return jsonify({"status": "error", "message": "API key not provided."})

if __name__ == "__main__":
    app.run(debug=True)
