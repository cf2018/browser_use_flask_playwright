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
                base_url='https://example.com',  # Set a base URL for navigation
                allowed_domains=['*'],  # Restrict navigation to trusted domains
                default_navigation_timeout=10000,  # Set navigation timeout to 30 seconds
                minimum_wait_page_load_time=0.25,  # Ensure a baseline wait time for page load
            )
            browser = Browser(config=browser_config)
            page = await browser.new_tab()  # Create a new tab object
            #await page.goto("https://www.google.com")  # Navigate using the tab object
            logging.info("Navigated to google.com")

            agent = Agent(
                task=task,
                llm=llm,
                browser=browser,
            )
            logging.info(f"Agent initialized with task: {task}")
            print("Starting agent...\n")


            # Execute the prompt directly
            history = await agent.run()

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

@app.route("/update_model", methods=["POST"])
def update_model():
    selected_model = request.form.get("gemini_model")
    if selected_model:
        os.environ["GEMINI_MODEL"] = selected_model
        logging.info(f"Gemini model updated to: {selected_model}")
        return jsonify({"status": "success", "message": "Model updated."})
    return jsonify({"status": "error", "message": "Model not provided."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
