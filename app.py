import os
import json
from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO
from dotenv import load_dotenv
from language_learning_bot import LanguageLearningBot
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "language-learning-secret-key")
socketio = SocketIO(app)

# Global dictionary to store user bots
user_bots = {}

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/api/start-session', methods=['POST'])
def start_session():
    """Initialize a new language learning session"""
    data = request.json
    
    # Create a unique session ID
    session_id = os.urandom(16).hex()
    session['session_id'] = session_id
    
    # Create a new bot instance for this session
    bot = LanguageLearningBot()
    bot.user_name = data.get('name', 'User')
    bot.native_language = data.get('native_language')
    bot.learning_language = data.get('learning_language')
    bot.selected_scene = data.get('scenario', 'restaurant')
    
    # Store the bot in the global dictionary
    user_bots[session_id] = bot
    
    # Create welcome message
    welcome_message = f"Hello {bot.user_name}! Let's practice {bot.learning_language} in a {bot.selected_scene} scenario. I'll help you learn and provide feedback on your language use. Feel free to start the conversation!"
    
    return jsonify({
        'success': True,
        'message': welcome_message
    })

@app.route('/api/send-message', methods=['POST'])
def send_message():
    """Process a user message and return the bot's response"""
    data = request.json
    session_id = session.get('session_id')
    user_input = data.get('message', '')
    
    # Check if session exists
    if not session_id or session_id not in user_bots:
        return jsonify({
            'success': False,
            'message': 'Session not found or expired. Please start a new session.'
        }), 404
    
    bot = user_bots[session_id]
    
    try:
        # Add to conversation history
        bot.conversation_history.append({"role": "user", "content": user_input})
        
        # Check for mistakes
        mistakes = []
        if len(bot.conversation_history) > 1:
            try:
                mistake_info = bot.check_for_mistakes(user_input)
                if mistake_info and mistake_info.get('has_mistakes', False):
                    mistakes = mistake_info.get('mistakes', [])
            except Exception as e:
                print(f"Error checking mistakes: {str(e)}")
        
        # Create conversation chain if it doesn't exist
        if not hasattr(bot, 'conversation_chain'):
            conversation_prompt = ChatPromptTemplate.from_messages([
                ("system", bot.create_system_prompt()),
                ("human", "{input}")
            ])
            
            bot.conversation_chain = LLMChain(
                llm=bot.llm,
                prompt=conversation_prompt,
                verbose=False
            )
        
        # Get full conversation history for context
        full_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in bot.conversation_history])
        
        # Get response from the assistant
        response = bot.conversation_chain.invoke({"input": user_input + "\n\nConversation history:\n" + full_history})
        bot_response = response["text"]
        
        # Add to conversation history
        bot.conversation_history.append({"role": "assistant", "content": bot_response})
        
        return jsonify({
            'success': True,
            'response': bot_response,
            'mistakes': mistakes
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error processing message: {str(e)}'
        }), 500

@app.route('/api/get-review', methods=['GET'])
def get_review():
    """Generate a review of the user's performance"""
    session_id = session.get('session_id')
    
    # Check if session exists
    if not session_id or session_id not in user_bots:
        return jsonify({
            'status': 'error',
            'message': 'Session not found or expired. Please start a new session.'
        }), 404
    
    bot = user_bots[session_id]
    
    try:
        if not bot.mistakes:
            review = {
                'status': 'success',
                'no_mistakes': True,
                'message': "Great job! You didn't make any mistakes in this conversation."
            }
        else:
            # Organize mistakes by category
            categories = {}
            for mistake in bot.mistakes:
                category = mistake.get("category", "Uncategorized")
                if category not in categories:
                    categories[category] = []
                categories[category].append(mistake)
            
            # Get improvement suggestions
            suggestion_prompt = ChatPromptTemplate.from_messages([
                ("system", f"""
                You are a language learning coach specializing in {bot.learning_language}.
                Based on the mistakes the user made during their conversation, provide:
                1. 2-3 specific exercises or activities to improve in each category
                2. Any resources (like apps, websites, or books) that would help with these specific areas
                3. A short motivational message to encourage continued learning
                
                Keep your response concise and practical.
                """),
                ("human", str(categories))
            ])
            
            suggestion_chain = LLMChain(
                llm=bot.llm,
                prompt=suggestion_prompt,
                verbose=False
            )
            
            suggestions = suggestion_chain.invoke({"input": str(categories)})
            
            review = {
                'status': 'success',
                'no_mistakes': False,
                'mistakes': bot.mistakes,
                'categories': {category: len(mistakes) for category, mistakes in categories.items()},
                'suggestions': suggestions["text"]
            }
        
        return jsonify(review)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': f'Error generating review: {str(e)}'
        }), 500

@app.route('/api/end-session', methods=['POST'])
def end_session():
    """End the current session"""
    session_id = session.get('session_id')
    
    if session_id and session_id in user_bots:
        # Clean up resources
        try:
            user_bots[session_id].db_manager.close()
        except:
            pass
        # Remove the bot instance
        del user_bots[session_id]
        session.pop('session_id', None)
    
    return jsonify({
        'success': True,
        'message': 'Session ended successfully'
    })

if __name__ == '__main__':
    # Create the templates and static directories if they don't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    # Start the Flask app
    socketio.run(app, debug=True) 