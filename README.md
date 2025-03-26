# Language Learning Chatbot

An interactive chatbot designed to help users practice and improve their language skills through conversation.

## Features

- **Interactive Conversations**: Practice language skills in various scenarios
- **Real-time Feedback**: Get immediate corrections on grammar, vocabulary, and more
- **Performance Review**: Receive a summary of mistakes and personalized improvement suggestions
- **User-friendly Interface**: Modern web interface for an engaging learning experience
- **Customizable Learning**: Select your native language, target language, and proficiency level

## Requirements

- Python 3.8 or higher
- OpenAI API key

## Installation

1. Clone this repository to your local machine
2. Create a virtual environment:
   ```
   python -m venv .venv
   ```
3. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - macOS/Linux: `source .venv/bin/activate`
4. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
5. Create a `.env` file based on the `.env.template` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   OPENAI_MODEL=gpt-4-turbo-preview  # or another suitable model
   ```

## Running the Application

### Web Interface

Start the web application:
```
python app.py
```

Then open your browser and navigate to:
```
http://127.0.0.1:5000
```

### Command Line Interface

If you prefer to use the command-line interface:
```
python language_learning_bot.py
```

### Jupyter Notebook

To run the Jupyter notebook version:
```
jupyter notebook LanguageLearningBot.ipynb
```

## Usage

1. Enter your name, native language, and the language you want to practice
2. Select your proficiency level
3. Choose a conversation scenario
4. Start chatting with the bot in your target language
5. Receive real-time feedback on your mistakes
6. Get a performance review with personalized suggestions when you finish

## Troubleshooting

- **API Key Issues**: Ensure your OpenAI API key is valid and has sufficient credits
- **Model Availability**: Use `python check_models.py` to verify your API key has access to the model
- **Dependency Issues**: Make sure all requirements are installed with the correct versions

## Example Conversation

```
Welcome to the Language Learning Bot!
What's your name? John
What language do you speak natively? English
What language would you like to learn? Spanish

What's your current level in Spanish?
1. Beginner
2. Intermediate
3. Advanced
Enter the number corresponding to your level: 1

Select a scene for your conversation:
1. At a restaurant
2. Shopping at a store
3. Asking for directions
4. Meeting new people
5. At a hotel
Enter the number of your choice: 1

Great! We'll practice Spanish in a scenario: at a restaurant. 