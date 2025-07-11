#!/usr/bin/env python3
import asyncio
import os
from dotenv import load_dotenv
from browser_use import Agent, Browser, BrowserConfig
from browser_use.llm import ChatGoogle, UserMessage

# Load environment variables
load_dotenv()

# Set environment variable to skip LLM API key verification
os.environ["SKIP_LLM_API_KEY_VERIFICATION"] = "true"

async def main():
    try:
        # Check if GOOGLE_API_KEY is set
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            print("Error: GOOGLE_API_KEY environment variable is not set.")
            print("Please create a .env file with your GOOGLE_API_KEY or set it in your environment.")
            return
        
        # Configure the model to use Gemini
        print("Initializing Gemini model...")
        llm = ChatGoogle(model='gemini-2.0-flash-exp')
        
        # Test the LLM connection
        print("Testing LLM connection...")
        test_message = UserMessage(role="user", content="Hello")
        response = await llm.ainvoke([test_message])
        print(f"LLM test response: {response}")
        
        # Configure the browser to use Playwright
        browser_config = BrowserConfig(
            browser_type='chromium',  # Playwright uses 'chromium' by default
            headless=False,  # Set to False to see the browser in action
        )
        
        # Create the browser instance
        browser = Browser(config=browser_config)
        
        # Define the search task
        task = ''''1. go to mercadolibre.com.ar
                  2. search for "capibara mochila" 
                  3. filter only free shipping ( envio gratis )
                  4. extract the price and the link of the first 5 results
                  '''
     
        # Create and run the agent
        print("Starting browser automation to search...")
        agent = Agent(
            task=task,
            llm=llm,
            browser=browser,
        )
        
        # Run the agent and get results
        history = await agent.run()
        
        # Print the results
        print("\n--- SEARCH RESULTS ---")
        print(history.final_result())
        
        # Allow time to see results before closing
        input("Press Enter to close the browser...")
        await browser.close()
        
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
