# Language Learning Chatbot Documentation

## Overview

The Language Learning Chatbot is an interactive application designed to help users practice foreign languages by engaging in conversations with an AI assistant. The chatbot provides real-time feedback on language errors, offers corrections, and tracks progress over time.

## System Components

### 1. Language Learning Bot (`language_learning_bot.py`)

This is the core module that handles:
- User information collection
- Conversation management
- Mistake detection and correction
- Performance feedback generation

### 2. Database Manager (`db_manager.py`)

Responsible for:
- Creating and managing the SQLite database
- Storing user profiles and language settings
- Recording conversations and mistakes
- Generating reports on learning progress

### 3. Web Application (`app.py`)

The web interface that:
- Provides a modern, user-friendly UI/UX
- Handles user sessions and conversations
- Displays real-time mistake feedback
- Shows performance reviews and improvement suggestions

## Setup and Configuration

### Environment Variables

The system uses a `.env` file to store configuration settings:

```
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4-turbo-preview  # or another compatible model
SECRET_KEY=your_flask_secret_key  # for web session management
```

You can use the `.env.template` file as a starting point.

### Model Verification

Use the `check_models.py` script to verify that your API key has access to the required OpenAI models:

```
python check_models.py
```

## Usage

### Web Interface

1. Start the web application:
   ```
   python app.py
   ```

2. Open your browser and navigate to `http://127.0.0.1:5000`

3. On the onboarding screen:
   - Enter your name
   - Select your native language
   - Choose the language you want to practice
   - Set your proficiency level
   - Select a conversation scenario

4. On the chat screen:
   - Type messages in your target language
   - Receive responses from the AI tutor
   - View feedback on any mistakes you make

5. When you're ready to end the session:
   - Click the "End Session" button
   - Review your performance summary
   - See categorized mistakes and improvement suggestions
   - Start a new session if desired

### Command Line Interface

For users who prefer a terminal-based experience:

1. Run the CLI version:
   ```
   python language_learning_bot.py
   ```

2. Follow the prompts to set up your session.

3. Type messages in your target language and receive responses and feedback.

4. Type 'exit' to end the session and see your performance summary.

## Jupyter Notebook

For an interactive notebook experience:

1. Start Jupyter:
   ```
   jupyter notebook
   ```

2. Open `LanguageLearningBot.ipynb` and follow the guided cells.

## Extending the System

### Adding New Languages

The system supports any languages available through the OpenAI models. No specific configuration is needed to add new languages.

### Custom Conversation Scenarios

To add new conversation scenarios, update the available options in the web interface's HTML template.

### Enhanced Error Detection

The mistake detection algorithm can be customized by modifying the prompt templates in `language_learning_bot.py`.

## Technical Details

### Dependencies

The system relies on the following main packages:
- OpenAI API for language generation
- Flask for the web interface
- SQLite for database storage
- LangChain for conversation chains and prompt management

### Architecture

The application follows a layered architecture:
1. **Presentation Layer**: Web interface (Flask) or command-line interface
2. **Business Logic Layer**: LanguageLearningBot class with conversation and error detection
3. **Data Access Layer**: DatabaseManager for persistent storage

### Data Flow

1. User inputs are sent to the language learning bot
2. The bot processes the input through the OpenAI API
3. Responses and detected errors are returned to the user
4. All interactions are stored in the database for future reference

## Troubleshooting

### API Key Issues

If you encounter errors related to the OpenAI API:
- Verify your API key is correct in the `.env` file
- Check that your account has sufficient credits
- Ensure you have access to the model specified in the configuration

### Database Issues

If the database is not working correctly:
- Check file permissions for the `language_learning.db` file
- Verify the database schema with `sqlite3 language_learning.db .schema`
- Ensure the application has write access to the directory

### Web Interface Issues

If the web interface is not working:
- Check that all required packages are installed
- Verify that the Flask server is running on the expected port
- Ensure that all static files (CSS, JS) are properly loaded 