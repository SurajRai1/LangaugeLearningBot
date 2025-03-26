import os
import openai
import json
import traceback
from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from db_manager import MistakeTracker

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

class LanguageLearningBot:
    def __init__(self):
        self.user_name = ""
        self.native_language = ""
        self.learning_language = ""
        self.proficiency_level = ""
        self.selected_scene = ""
        self.conversation_history = []
        self.mistakes = []
        self.session_start_time = None
        self.vocabulary_learned = set()
        self.consecutive_correct_responses = 0
        self.learning_streak = 0
        
        try:
            # Initialize LLM with model from environment variable
            self.llm = ChatOpenAI(
                model_name=os.getenv("LANGUAGE_MODEL", "gpt-3.5-turbo"),
                temperature=float(os.getenv("TEMPERATURE", 0.7)),
            )
            
            # Initialize database manager
            self.db_manager = MistakeTracker("language_learning.db")
        except Exception as e:
            print(f"Error initializing bot: {str(e)}")
            raise
        
    def start_session(self):
        """Start a new language learning session by gathering user information"""
        try:
            print("Welcome to the Language Learning Bot!")
            self.user_name = input("What's your name? ")
            self.native_language = input("What language do you speak natively? ")
            
            # Get the language the user wants to learn
            self.learning_language = input("What language would you like to learn? ")
            
            # Get the user's proficiency level
            print("\nWhat's your current level in " + self.learning_language + "?")
            print("1. Beginner")
            print("2. Intermediate")
            print("3. Advanced")
            level_choice = input("Enter the number corresponding to your level: ")
            
            if level_choice == "1":
                self.proficiency_level = "beginner"
            elif level_choice == "2":
                self.proficiency_level = "intermediate"
            elif level_choice == "3":
                self.proficiency_level = "advanced"
            else:
                print("Invalid choice, defaulting to beginner.")
                self.proficiency_level = "beginner"
            
            # Select a conversation scene
            self.select_scene()
            
            # Start the conversation
            self.have_conversation()
        except Exception as e:
            print(f"Error during session: {str(e)}")
            traceback.print_exc()
        
    def select_scene(self):
        """Allow the user to select a conversation scene"""
        print("\nSelect a scene for your conversation:")
        print("1. At a restaurant")
        print("2. Shopping at a store")
        print("3. Asking for directions")
        print("4. Meeting new people")
        print("5. At a hotel")
        
        scene_choice = input("Enter the number of your choice: ")
        scenes = {
            "1": "at a restaurant",
            "2": "shopping at a store",
            "3": "asking for directions",
            "4": "meeting new people",
            "5": "at a hotel"
        }
        
        self.selected_scene = scenes.get(scene_choice, "at a restaurant")
        print(f"\nGreat! We'll practice {self.learning_language} in a scenario: {self.selected_scene}.")
    
    def create_system_prompt(self):
        """Create the system prompt for the language learning conversation"""
        system_prompt = f"""
        You are an expert language learning assistant helping someone learn {self.learning_language}. 
        Their native language is {self.native_language} and their proficiency level is {self.proficiency_level}.
        
        The conversation will be set in this scenario: {self.selected_scene}.
        
        Follow these rules strictly to create an exceptional learning experience:

        1. Language Usage and Encouragement:
           - ALWAYS respond primarily in {self.learning_language}
           - Provide {self.native_language} translations in parentheses for new phrases
           - When user speaks in {self.native_language}:
             * Provide the {self.learning_language} translation of their message
             * Give 2-3 alternative ways to express the same thing
             * Encourage them to repeat one of these phrases
           - Adapt language complexity to their {self.proficiency_level} level
           - Gradually introduce new vocabulary and phrases

        2. Mistake Handling:
           - When mistakes occur:
             * Highlight the mistake gently but clearly
             * Provide the correction
             * Explain the grammar rule/reason in {self.native_language}
             * Give 2 example sentences using the correct form
             * Encourage them to try again with the correct form

        3. Interactive Learning:
           - Ask follow-up questions to encourage conversation
           - Create mini-challenges (e.g., "Try to order using these new words")
           - Provide positive reinforcement for correct usage
           - Use emojis and formatting to make corrections clear and friendly

        4. Cultural Context:
           - Include relevant cultural information about {self.learning_language}-speaking regions
           - Explain idioms and common expressions
           - Share context about social norms and customs

        5. Progress Tracking:
           - Note new vocabulary items the user learns
           - Recognize when they correctly use previously challenging phrases
           - Provide periodic mini-progress updates

        6. Scenario Immersion:
           - Stay in character for the {self.selected_scene} scenario
           - Create realistic dialogue situations
           - Introduce typical vocabulary for this context
           - Guide user through common interactions in this setting

        Remember to keep the conversation engaging, natural, and encouraging while maintaining a clear focus on learning.
        """
        return system_prompt
    
    def have_conversation(self):
        """Have a conversation with the user in the learning language"""
        try:
            system_prompt = self.create_system_prompt()
            
            # Create conversation template
            conversation_prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "{input}")
            ])
            
            # Create conversation chain
            conversation_chain = LLMChain(
                llm=self.llm,
                prompt=conversation_prompt,
                verbose=True
            )
            
            # Initialize the conversation
            response = conversation_chain.invoke({"input": f"Hi, I'm {self.user_name}. I'm here to practice {self.learning_language}."})
            print("\nAssistant:", response["text"])
            
            # Add to conversation history
            self.conversation_history.append({"role": "assistant", "content": response["text"]})
            
            # Main conversation loop
            while True:
                user_input = input("\nYou (type 'exit' to end): ")
                
                if user_input.lower() == 'exit':
                    break
                    
                # Add to conversation history
                self.conversation_history.append({"role": "user", "content": user_input})
                
                # Check for mistakes and provide feedback using a separate LLM call
                if len(self.conversation_history) > 1:
                    self.check_for_mistakes(user_input)
                
                try:
                    # Get response from the assistant
                    full_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in self.conversation_history])
                    response = conversation_chain.invoke({"input": user_input + "\n\nConversation history:\n" + full_history})
                    
                    print("\nAssistant:", response["text"])
                    
                    # Add to conversation history
                    self.conversation_history.append({"role": "assistant", "content": response["text"]})
                except Exception as e:
                    print(f"\nError getting response: {str(e)}")
                    print("Let's continue the conversation.")
            
            # Provide review and feedback at the end
            self.provide_review()
        except Exception as e:
            print(f"Error in conversation: {str(e)}")
            traceback.print_exc()
    
    def check_for_mistakes(self, user_input):
        """Enhanced mistake checking with detailed feedback"""
        mistake_prompt = ChatPromptTemplate.from_messages([
            ("system", f"""
            You are an expert language teacher analyzing text in {self.learning_language}.
            The user's native language is {self.native_language} and their proficiency level is {self.proficiency_level}.
            
            Provide a comprehensive analysis of the user's input:
            1. Check for all types of mistakes:
               - Grammar
               - Vocabulary
               - Pronunciation (if relevant)
               - Word order
               - Conjugation
               - Articles/Gender
               - Register/Formality
            
            2. For each mistake found, provide:
               - The incorrect portion
               - The correction
               - A detailed explanation in {self.native_language}
               - The specific rule being applied
               - Common pitfalls related to this mistake
               - 2 example sentences showing correct usage
            
            Format your response as JSON:
            {{
                "has_mistakes": true/false,
                "mistakes": [
                    {{
                        "mistake": "incorrect text",
                        "correction": "corrected text",
                        "explanation": "detailed explanation",
                        "rule": "grammar rule or pattern",
                        "category": "grammar/vocabulary/etc.",
                        "examples": ["example1", "example2"],
                        "common_pitfalls": "related mistakes to watch for"
                    }}
                ],
                "positive_feedback": "what the user did well",
                "learning_tips": "specific suggestions for improvement"
            }}
            """),
            ("human", user_input)
        ])
        
        mistake_chain = LLMChain(
            llm=self.llm,
            prompt=mistake_prompt,
            verbose=False
        )
        
        try:
            # Get mistake analysis
            mistake_analysis = mistake_chain.invoke({"input": user_input})
            mistake_text = mistake_analysis.get("text", "{}")
            
            # Parse the JSON response
            mistake_data = json.loads(mistake_text)
            
            if mistake_data.get("has_mistakes", False):
                for mistake in mistake_data.get("mistakes", []):
                    # Add to the mistake list
                    self.mistakes.append(mistake)
                    
                    # Save to database
                    self.db_manager.add_mistake(
                        self.user_name,
                        self.learning_language,
                        mistake.get("mistake", ""),
                        mistake.get("correction", ""),
                        mistake.get("explanation", ""),
                        mistake.get("category", "")
                    )
        except Exception as e:
            print(f"Error analyzing mistakes: {str(e)}")
            # If there's an error parsing the response, just continue
            pass
    
    def provide_review(self):
        """Enhanced review with comprehensive feedback"""
        if not self.mistakes:
            print("\n🌟 Excellent work! You maintained a perfect conversation in {self.learning_language}!")
            return
        
        print("\n=== Comprehensive Language Learning Review ===")
        
        # Organize mistakes by category
        categories = {}
        for mistake in self.mistakes:
            category = mistake.get("category", "Uncategorized")
            if category not in categories:
                categories[category] = []
            categories[category].append(mistake)
        
        # Print detailed analysis
        print("\n📊 Performance Analysis:")
        for category, mistakes in categories.items():
            print(f"\n{category.upper()} ({len(mistakes)} mistakes):")
            for i, mistake in enumerate(mistakes, 1):
                print(f"\n{i}. Original: {mistake.get('mistake', '')}")
                print(f"   ✓ Correction: {mistake.get('correction', '')}")
                print(f"   📝 Rule: {mistake.get('rule', '')}")
                print(f"   💡 Explanation: {mistake.get('explanation', '')}")
                if mistake.get('examples'):
                    print("   📚 Examples:")
                    for example in mistake.get('examples', []):
                        print(f"      - {example}")
        
        # Calculate progress metrics
        total_interactions = len(self.conversation_history) // 2
        mistake_rate = len(self.mistakes) / total_interactions
        
        print("\n📈 Progress Metrics:")
        print(f"- Total Interactions: {total_interactions}")
        print(f"- Accuracy Rate: {(1 - mistake_rate) * 100:.1f}%")
        print(f"- New Vocabulary Learned: {len(self.vocabulary_learned)} words/phrases")
        print(f"- Learning Streak: {self.learning_streak} correct responses")
        
        # Get improvement suggestions
        self.get_improvement_suggestions(categories)
    
    def get_improvement_suggestions(self, categories):
        """Generate detailed improvement suggestions"""
        suggestion_prompt = ChatPromptTemplate.from_messages([
            ("system", f"""
            You are an expert language coach specializing in {self.learning_language}.
            Create a comprehensive improvement plan based on the user's mistakes:

            1. For each mistake category:
               - Provide 3 targeted exercises
               - Suggest specific practice activities
               - Recommend learning resources
               
            2. Create a structured study plan:
               - Daily practice suggestions
               - Weekly learning goals
               - Recommended time allocation
               
            3. Provide resource recommendations:
               - Apps and websites
               - Books and materials
               - Practice partners or language exchange
               - Online courses or videos
               
            4. Include a motivational message that:
               - Acknowledges progress made
               - Encourages continued practice
               - Sets realistic expectations
               - Highlights benefits of mastering these areas

            Make suggestions practical and actionable.
            """),
            ("human", str(categories))
        ])
        
        suggestion_chain = LLMChain(
            llm=self.llm,
            prompt=suggestion_prompt,
            verbose=False
        )
        
        suggestions = suggestion_chain.invoke({"input": str(categories)})
        print("\n🎯 Personalized Improvement Plan")
        print(suggestions["text"])
        
        print("\n💪 Remember:")
        print("- Every mistake is a learning opportunity")
        print("- Consistent practice leads to improvement")
        print("- You're making progress with each conversation!")
        
        # Save session statistics to database
        self.db_manager.save_session_stats(
            self.user_name,
            self.learning_language,
            len(self.mistakes),
            len(self.vocabulary_learned),
            self.learning_streak
        )

if __name__ == "__main__":
    try:
        bot = LanguageLearningBot()
        bot.start_session()
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        traceback.print_exc() 