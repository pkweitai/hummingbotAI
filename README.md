# ![Alt text](ai.png?raw=true "Title") Hummingbot AI Chatbot 

![Alt text](tg.png?raw=true "Title")
## Description
This project introduces a Telegram chatbot powered by a Large Language Model (LLM), specifically designed for interacting with Hummingbot. It leverages MQTT for command execution and incorporates a robust, production-ready architecture using HayStack and Google Gemini, offering easy adaptability to other LLMs like OpenAI.

## Features
- **Comprehensive Command Execution**: Fully exercise all available commands via MQTT.
- **Flexible Architecture**: Built with HayStack and Google Gemini, making it easy to switch to other LLMs.
- **Production-Ready**: Ready for deployment with built-in scalability and reliability.
- **Scalable Tool feature : you can create new tools by adding more featuretable with different bottypes, to make the AiBot smarter to capture actions for users (e.g. get specific news on crypto topic, get market sentiments or synthesis a trading strategies) - this is still in Alpha , need more community support

## Requirements
To set up the chatbot, follow these steps:

1. **Export Google API Key**
   Ensure that the Google API Key is set in your environment:
   ```bash
   export GOOGLE_API_KEY='your_google_api_key_here'
   ```

2 **Running Hummingbot**
   Clone and set up Hummingbot from the official repository:
   ```bash
   git clone https://github.com/hummingbot/hummingbot.git
   cd hummingbot
   ```

# Follow the setup instructions in the Hummingbot repository

3 **Running MQTT Broker**
Set up an MQTT Broker by cloning the broker repository:
   ```bash
    git clone git@github.com:hummingbot/brokers.git
    cd brokers
   ```

4 **Follow the setup instructions for the broker**
- Create a Telegram Bot
Create a Telegram bot using BotFather on Telegram and obtain the bot token:
- Start a chat with BotFather (@BotFather)
- Follow the instructions to create a new bot and get your token

## Installation
After setting up the requirements, install the necessary dependencies:

   ```bash
    pip install -r requirements.txt
    python aihbot.py
   ```

## TODO
- Support More LLMs: Integrate additional LLM providers like OpenAI, Groq, and LLAMA3.
- Improve Chat Performance: Implement a Context Memory based Agent to enhance chat interactions.
- Add More Features:
  Expand capabilities to include more trading and crypto-related features.
- Add web widgets to enable advanced strategy , charting  

## Contributing
Contributions are welcome! Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests to us.

## License
This project is licensed under the MIT License - see the LICENSE.md file for details.
