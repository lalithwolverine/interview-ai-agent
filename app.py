from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import requests
from dotenv import load_dotenv
import json
import re
import random
from datetime import datetime
from pathlib import Path
import google.generativeai as genai
from llmPrompts import get_question_prompt, get_evaluation_prompt, format_evaluation_context

load_dotenv()

app = Flask(__name__)
CORS(app)

# Security: Check for API key
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyCRGu_2qIz7xw4OyeoruaAGeh1LqbiG-t8')
if not GEMINI_API_KEY:
    print("ERROR: GEMINI_API_KEY not found in environment variables.")
    print("Please create a .env file with: GEMINI_API_KEY=your_key_here")
    exit(1)

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)
GEMINI_MODEL = 'gemini-1.5-flash'  # Using flash for faster responses
GEMINI_MAX_TOKENS = 200  # Conservative limit for JSON responses
GEMINI_TIMEOUT = 30

# Create data directory if it doesn't exist
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# Interview state management
interview_sessions = {}

# Evaluation schema
EVALUATION_SCHEMA = {
    "scores": {"communication": 0, "technical": 0, "examples": 0},
    "overall": 0,
    "should_followup": False,
    "followup_question": "",
    "feedback": []
}

class QuestionBank:
    """Curated question bank with difficulty buckets"""
    def __init__(self):
        self.questions = {
            'engineer': {
                'easy': [
                    "Tell me about yourself and your experience with software development.",
                    "What programming languages are you most comfortable with?",
                    "Describe your experience with version control systems like Git."
                ],
                'medium': [
                    "Describe a challenging project you worked on and how you solved it.",
                    "How do you approach debugging a complex issue?",
                    "What's your approach to code review and collaboration?",
                    "How do you stay updated with new technologies?"
                ],
                'hard': [
                    "Design a scalable system architecture for handling 1 million requests per second.",
                    "Explain how you would optimize a slow database query affecting production.",
                    "Describe a time when you had to make a critical technical decision under pressure.",
                    "How would you handle a security vulnerability discovered in production code?"
                ]
            },
            'sales': {
                'easy': [
                    "Tell me about yourself and your sales experience.",
                    "How do you approach building relationships with new clients?",
                    "What motivates you in a sales role?"
                ],
                'medium': [
                    "Describe a time when you closed a difficult sale.",
                    "How do you handle rejection in sales?",
                    "What's your strategy for identifying potential customers?",
                    "How do you prioritize your leads and manage your sales pipeline?"
                ],
                'hard': [
                    "Describe a situation where you had to overcome a major customer objection that seemed insurmountable.",
                    "How would you approach a client who has been with a competitor for 10 years?",
                    "Explain your strategy for negotiating a complex multi-year enterprise deal.",
                    "How do you handle a situation where a client threatens to leave due to pricing?"
                ]
            },
            'retail': {
                'easy': [
                    "Tell me about yourself and why you're interested in retail.",
                    "How would you handle a difficult or angry customer?",
                    "What does excellent customer service mean to you?"
                ],
                'medium': [
                    "Describe your experience with cash handling and point-of-sale systems.",
                    "How do you stay motivated during slow periods?",
                    "How do you approach upselling products to customers?",
                    "Describe a time when you had to work as part of a team."
                ],
                'hard': [
                    "What would you do if you noticed a customer shoplifting?",
                    "Describe how you would handle a situation where multiple customers need assistance simultaneously.",
                    "How would you deal with a product return request that doesn't meet store policy?",
                    "Explain your approach to handling inventory discrepancies during a busy holiday season."
                ]
            }
        }
    
    def get_question(self, role, difficulty='medium', used_questions=None):
        """Get a random question from the specified difficulty bucket"""
        if used_questions is None:
            used_questions = []
        
        available = [q for q in self.questions[role][difficulty] if q not in used_questions]
        if not available:
            # If all questions used, reset
            available = self.questions[role][difficulty]
        
        return random.choice(available)

class HeuristicsAnalyzer:
    """Simple heuristics layer for answer analysis"""
    
    @staticmethod
    def analyze_answer(answer: str, role: str) -> dict:
        """Analyze answer using simple heuristics"""
        answer_lower = answer.lower()
        words = answer.split()
        word_count = len(words)
        
        # Profanity detection (simple)
        profanity_words = ['damn', 'hell', 'crap', 'stupid', 'idiot']  # Basic list
        has_profanity = any(word in answer_lower for word in profanity_words)
        
        # Off-topic detection (check for common off-topic phrases)
        off_topic_phrases = ['i don\'t know', 'i have no idea', 'not relevant', 'unrelated']
        is_off_topic = any(phrase in answer_lower for phrase in off_topic_phrases)
        
        # Answer quality indicators
        has_digits = bool(re.search(r'\d+', answer))
        has_keywords = HeuristicsAnalyzer._check_role_keywords(answer_lower, role)
        has_examples = any(word in answer_lower for word in ['example', 'instance', 'time when', 'situation', 'project'])
        
        # Length analysis
        is_too_short = word_count < 10
        is_too_long = word_count > 200
        is_appropriate_length = 20 <= word_count <= 150
        
        # Determine if answer is strong
        is_strong = (
            is_appropriate_length and
            has_keywords and
            (has_examples or has_digits) and
            not has_profanity and
            not is_off_topic
        )
        
        return {
            'word_count': word_count,
            'has_digits': has_digits,
            'has_keywords': has_keywords,
            'has_examples': has_examples,
            'has_profanity': has_profanity,
            'is_off_topic': is_off_topic,
            'is_strong': is_strong,
            'is_too_short': is_too_short,
            'is_too_long': is_too_long
        }
    
    @staticmethod
    def _check_role_keywords(answer: str, role: str) -> bool:
        """Check if answer contains role-relevant keywords"""
        role_keywords = {
            'engineer': ['code', 'programming', 'develop', 'debug', 'algorithm', 'system', 'software', 'project', 'api', 'database'],
            'sales': ['customer', 'client', 'relationship', 'close', 'deal', 'revenue', 'target', 'pipeline', 'prospect', 'negotiation'],
            'retail': ['customer', 'service', 'product', 'store', 'experience', 'satisfaction', 'help', 'assist', 'purchase', 'inventory']
        }
        keywords = role_keywords.get(role, [])
        return any(keyword in answer for keyword in keywords)
    
    @staticmethod
    def is_nonsense(answer: str) -> bool:
        """Detect nonsense inputs"""
        answer = answer.strip()
        
        # Too short
        if len(answer) < 3:
            return True
        
        # Only special characters
        if not re.search(r'[a-zA-Z]', answer):
            return True
        
        # Repetitive characters
        if len(set(answer)) < 3 and len(answer) > 10:
            return True
        
        # Common nonsense patterns
        nonsense_patterns = ['asdf', 'qwerty', 'test', '12345', 'abc', 'xyz']
        if answer.lower() in nonsense_patterns:
            return True
        
        return False

class LLMService:
    """Service for interacting with Google Gemini LLM"""
    
    def __init__(self):
        self.model = genai.GenerativeModel(GEMINI_MODEL)
    
    def call_gemini_api(self, prompt: str, max_tokens: int = GEMINI_MAX_TOKENS, temperature: float = 0.7) -> str:
        """Call Gemini API with retry logic"""
        max_retries = 3
        
        # Create generation config as dict (more compatible)
        generation_config = {
            "temperature": temperature,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": max_tokens,
        }
        
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=generation_config
                )
                
                if response and hasattr(response, 'text') and response.text:
                    generated_text = response.text.strip()
                    # Check if response is too long (token control)
                    if len(generated_text) > max_tokens * 4:  # Rough estimate
                        raise ValueError("Response exceeds expected size")
                    return generated_text
                else:
                    raise Exception("Empty response from Gemini API")
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2)
                    continue
                print(f"Error calling Gemini API: {e}")
                raise
        
        return ""
    
    def generate_followup_question(self, role: str, question: str, answer: str) -> str:
        """Generate follow-up question using LLM"""
        prompt = f"""{get_question_prompt(role)}

Previous question: {question}
Candidate's answer: {answer}

Generate a focused follow-up question (6-20 words):"""
        
        try:
            response = self.call_gemini_api(prompt, max_tokens=50, temperature=0.8)
            # Clean response
            response = response.strip()
            # Remove quotes if present
            response = response.strip('"').strip("'")
            # Take first sentence only
            response = response.split('.')[0].strip()
            if not response.endswith('?'):
                response += '?'
            return response
        except Exception as e:
            print(f"Error generating follow-up: {e}")
            return "Can you provide more specific details about that?"
    
    def evaluate_answer(self, question: str, answer: str, role: str) -> dict:
        """Evaluate answer using LLM and return JSON"""
        context = format_evaluation_context(question, answer, role)
        prompt = f"""{get_evaluation_prompt()}

{context}"""
        
        try:
            response = self.call_gemini_api(prompt, max_tokens=GEMINI_MAX_TOKENS, temperature=0.3)
            
            # Extract JSON from response
            json_match = re.search(r'\{[^{}]*"scores"[^{}]*\{[^{}]*\}[^{}]*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                # Try to find any JSON object
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    raise ValueError("No JSON found in response")
            
            # Parse JSON
            eval_data = json.loads(json_str)
            
            # Validate schema
            if not all(key in eval_data for key in EVALUATION_SCHEMA.keys()):
                raise ValueError("Invalid evaluation schema")
            
            # Ensure scores are in range
            for key in ['communication', 'technical', 'examples']:
                if key in eval_data.get('scores', {}):
                    eval_data['scores'][key] = max(0, min(5, int(eval_data['scores'][key])))
            
            # Ensure overall is 0-100
            if 'overall' in eval_data:
                eval_data['overall'] = max(0, min(100, int(eval_data['overall'])))
            
            return eval_data
            
        except Exception as e:
            print(f"Error evaluating answer: {e}")
            # Return default evaluation
            return {
                "scores": {"communication": 3, "technical": 3, "examples": 3},
                "overall": 60,
                "should_followup": True,
                "followup_question": "Can you elaborate on that?",
                "feedback": ["Evaluation temporarily unavailable"]
            }

class InterviewAgent:
    """Main interview agent with agentic behavior"""
    
    def __init__(self):
        self.question_bank = QuestionBank()
        self.heuristics = HeuristicsAnalyzer()
        self.llm_service = LLMService()
    
    def decide_followup(self, answer: str, question: str, role: str, session: dict):
        """Decide whether to force follow-up or ask LLM, return (should_followup, followup_question)"""
        heuristic_result = self.heuristics.analyze_answer(answer, role)
        answer_lower = answer.lower()
        
        # Enhanced off-topic detection - check FIRST before anything else
        off_topic_patterns = [
            'what is the weather', 'what time is it', 'what is the date', 'what day is it',
            'can you write', 'can you create', 'write me a resume', 'create a resume',
            'what is 2+2', 'calculate', 'tell me a joke', 'how are you',
            'what can you do', 'what are your capabilities', 'who are you',
            'what is your name', 'where are you from'
        ]
        
        # Check if clearly off-topic (contains off-topic pattern AND no interview-related words)
        interview_keywords = ['interview', 'question', 'answer', 'role', 'engineer', 'software', 'sales', 
                             'retail', 'customer', 'code', 'project', 'experience', 'work', 'job', 'position']
        is_clearly_off_topic = any(pattern in answer_lower for pattern in off_topic_patterns) and \
                               not any(keyword in answer_lower for keyword in interview_keywords)
        
        if is_clearly_off_topic:
            return (False, f"Let's focus on the interview. {question}")
        
        # Handle nonsense inputs
        if self.heuristics.is_nonsense(answer):
            return (False, f"I didn't quite understand that. Let's refocus on the interview question: {question}")
        
        # Check for profanity or off-topic
        if heuristic_result['has_profanity'] or heuristic_result['is_off_topic']:
            return (False, f"Let's keep our discussion professional and focused on the interview. {question}")
        
        # Only ask for elaboration if answer is EXTREMELY short (less than 5 words)
        # This prevents asking to elaborate on every question
        if heuristic_result['word_count'] < 5:
            return (True, "Could you please provide a more detailed answer?")
        
        # Don't force follow-up for moderately short answers - let LLM decide
        # Only force if answer is very short AND completely lacks substance
        if heuristic_result['word_count'] < 10 and not heuristic_result['has_keywords'] and not heuristic_result['has_examples']:
            return (True, "Can you provide more context about your experience?")
        
        # If answer is strong, check if we should escalate difficulty
        if heuristic_result['is_strong']:
            # Track strong answers
            if 'strong_answer_count' not in session:
                session['strong_answer_count'] = 0
            session['strong_answer_count'] += 1
            
            # After 3 strong answers, escalate difficulty
            if session['strong_answer_count'] >= 3 and session.get('difficulty', 'medium') != 'hard':
                session['difficulty'] = 'hard'
                session['strong_answer_count'] = 0  # Reset counter
                return (False, None)  # Signal to ask harder question
        
        # Use LLM to decide if follow-up is needed (only for substantial answers)
        # Skip LLM for very short answers (already handled above)
        # IMPORTANT: Only use LLM follow-up if answer is substantial but clearly incomplete
        if heuristic_result['word_count'] >= 15:
            # Check if answer is substantial but might need clarification
            # Only follow up if answer lacks BOTH examples AND keywords (very rare)
            if not heuristic_result['has_examples'] and not heuristic_result['has_keywords']:
                try:
                    eval_result = self.llm_service.evaluate_answer(question, answer, role)
                    should_followup = eval_result.get('should_followup', False)
                    followup_question = eval_result.get('followup_question', '')
                    
                    # Only follow up if LLM strongly suggests it AND provides a good question
                    # AND the overall score is low (indicating incomplete answer)
                    overall_score = eval_result.get('overall', 100)
                    if should_followup and followup_question and len(followup_question) > 10 and overall_score < 50:
                        return (True, followup_question)
                except Exception as e:
                    print(f"Error in LLM evaluation: {e}")
        
        # Default: move to next question (no follow-up needed)
        # Most answers are adequate - don't over-ask for elaboration
        return (False, None)

def save_session(session_id: str, session: dict):
    """Save session to JSON file"""
    try:
        session_file = DATA_DIR / f"{session_id}.json"
        
        # Prepare session data
        session_data = {
            "sessionId": session_id,
            "role": session.get('role'),
            "mode": "interview",
            "startedAt": session.get('started_at'),
            "events": [],
            "aggregatedFeedback": {}
        }
        
        # Convert conversation history to events
        for event in session.get('conversation_history', []):
            event_data = {
                "time": event.get('timestamp'),
                "speaker": event.get('role'),
                "text": event.get('content')
            }
            
            # Add evaluation if available
            if 'eval' in event:
                event_data['eval'] = event['eval']
            
            session_data['events'].append(event_data)
        
        # Add aggregated feedback if available
        if 'aggregated_feedback' in session:
            session_data['aggregatedFeedback'] = session['aggregated_feedback']
        
        # Write to file
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
        
    except Exception as e:
        print(f"Error saving session: {e}")

# Initialize agent
agent = InterviewAgent()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '').strip()
    session_id = data.get('session_id', 'default')
    
    # Handle empty message (silent user)
    if not user_message:
        return jsonify({
            'response': "I'm here to help you practice for interviews. Please type a message to continue, or select a role to begin.",
            'session_id': session_id
        })
    
    # Initialize or get session
    if session_id not in interview_sessions:
        interview_sessions[session_id] = {
            'role': None,
            'difficulty': 'medium',
            'current_question': None,
            'conversation_history': [],
            'questions_asked': [],
            'used_questions': [],
            'strong_answer_count': 0,
            'started_at': datetime.now().isoformat(),
            'aggregated_feedback': {}
        }
    
    session = interview_sessions[session_id]
    
    user_lower = user_message.lower()
    
    # Enhanced off-topic detection - check before processing
    if session.get('role') and session.get('current_question'):
        off_topic_patterns = [
            'what is the weather', 'what time is it', 'what is the date', 'what day is it',
            'can you write', 'can you create', 'write me a resume', 'create a resume',
            'what is 2+2', 'calculate', 'tell me a joke', 'joke',
            'how are you', 'what can you do', 'what are your capabilities',
            'who are you', 'what is your name', 'where are you from'
        ]
        interview_keywords = ['interview', 'question', 'answer', 'role', 'engineer', 'software', 
                            'sales', 'retail', 'customer', 'code', 'project', 'experience', 
                            'work', 'job', 'position', 'company', 'team']
        
        is_off_topic = any(pattern in user_lower for pattern in off_topic_patterns)
        has_interview_context = any(keyword in user_lower for keyword in interview_keywords)
        
        # Check if it's clearly off-topic and not related to interview
        if is_off_topic and not has_interview_context:
            current_q = session.get('current_question', 'Please answer the interview question.')
            response = f"I'm here to help you practice for interviews. Let's focus on that.\n\n{current_q}"
            session['conversation_history'].append({
                'role': 'user',
                'content': user_message,
                'timestamp': datetime.now().isoformat()
            })
            session['conversation_history'].append({
                'role': 'assistant',
                'content': response,
                'timestamp': datetime.now().isoformat()
            })
            return jsonify({
                'response': response,
                'session_id': session_id,
                'role': session['role'],
                'question_number': len(session['used_questions'])
            })
    
    # Add user message to history
    session['conversation_history'].append({
        'role': 'user',
        'content': user_message,
        'timestamp': datetime.now().isoformat()
    })
    
    # Determine role if not set
    if not session['role']:
        if 'engineer' in user_lower or 'software' in user_lower:
            session['role'] = 'engineer'
        elif 'sales' in user_lower:
            session['role'] = 'sales'
        elif 'retail' in user_lower:
            session['role'] = 'retail'
        else:
            response = "I'm here to help you practice for job interviews. Which role would you like to practice for?\n\n• Software Engineer\n• Sales Representative\n• Retail Associate\n\nType the role name to get started."
            session['conversation_history'].append({
                'role': 'assistant',
                'content': response,
                'timestamp': datetime.now().isoformat()
            })
            return jsonify({
                'response': response,
                'session_id': session_id,
                'role': None
            })
    
    # Generate response based on interview state
    role = session['role']
    difficulty = session.get('difficulty', 'medium')
    
    # Check if we need to ask a new question
    if not session.get('current_question'):
        # Get new question from bank
        question = agent.question_bank.get_question(role, difficulty, session['used_questions'])
        session['current_question'] = question
        session['used_questions'].append(question)
        session['questions_asked'].append({
            'question': question,
            'user_response': None,
            'timestamp': datetime.now().isoformat()
        })
        response = question
    else:
        # We have a current question, check if user answered it
        current_question = session['current_question']
        
        # Check if user wants to skip
        if any(word in user_lower for word in ['next', 'skip', 'move on', 'done']):
            # Move to next question
            session['current_question'] = None
            if len(session['used_questions']) < 10:  # Limit questions
                question = agent.question_bank.get_question(role, difficulty, session['used_questions'])
                session['current_question'] = question
                session['used_questions'].append(question)
                session['questions_asked'].append({
                    'question': question,
                    'user_response': None,
                    'timestamp': datetime.now().isoformat()
                })
                response = question
            else:
                response = "Great job! We've completed the interview. Type 'feedback' to see your summary."
        else:
            # User provided an answer, decide on follow-up
            should_followup, followup_question = agent.decide_followup(
                user_message, current_question, role, session
            )
            
            # Update question record with answer
            for qa in session['questions_asked']:
                if qa['question'] == current_question and qa['user_response'] is None:
                    qa['user_response'] = user_message
                    qa['timestamp'] = datetime.now().isoformat()
                    break
            
            # Evaluate answer
            try:
                eval_result = agent.llm_service.evaluate_answer(current_question, user_message, role)
                # Store evaluation in conversation history
                session['conversation_history'][-1]['eval'] = eval_result
            except Exception as e:
                print(f"Evaluation error: {e}")
            
            if should_followup and followup_question:
                response = followup_question
            elif followup_question is None and difficulty == 'hard':
                # Difficulty escalated, ask hard question
                question = agent.question_bank.get_question(role, 'hard', session['used_questions'])
                session['current_question'] = question
                session['used_questions'].append(question)
                session['questions_asked'].append({
                    'question': question,
                    'user_response': None,
                    'timestamp': datetime.now().isoformat()
                })
                response = f"[Increased difficulty] {question}"
            else:
                # Move to next question
                session['current_question'] = None
                # Count questions with answers (not just asked)
                questions_with_answers = len([qa for qa in session['questions_asked'] if qa.get('user_response')])
                
                if questions_with_answers < 10:
                    question = agent.question_bank.get_question(role, difficulty, session['used_questions'])
                    session['current_question'] = question
                    session['used_questions'].append(question)
                    session['questions_asked'].append({
                        'question': question,
                        'user_response': None,
                        'timestamp': datetime.now().isoformat()
                    })
                    response = question
                else:
                    # Automatically provide feedback after 10 questions
                    feedback_summary = generate_feedback_summary(session)
                    session['aggregated_feedback'] = {
                        'generated_at': datetime.now().isoformat(),
                        'summary': feedback_summary
                    }
                    response = f"Great job! You've completed 10 interview questions.\n\n{feedback_summary}"
    
    # Handle feedback request (if not already provided)
    if ('feedback' in user_lower or 'summary' in user_lower) and not session.get('aggregated_feedback'):
        response = generate_feedback_summary(session)
        session['aggregated_feedback'] = {
            'generated_at': datetime.now().isoformat(),
            'summary': response
        }
    
    # Add assistant response to history
    session['conversation_history'].append({
        'role': 'assistant',
        'content': response,
        'timestamp': datetime.now().isoformat()
    })
    
    # Save session periodically
    if len(session['conversation_history']) % 5 == 0:
        save_session(session_id, session)
    
    # Calculate total questions (target is 10) and current question number
    total_questions = 10
    questions_with_answers = len([qa for qa in session['questions_asked'] if qa.get('user_response')])
    
    # If we have a current question that hasn't been answered yet, show that number
    if session.get('current_question'):
        current_question_num = questions_with_answers + 1
    else:
        # No current question means we're between questions or done
        current_question_num = questions_with_answers
    
    return jsonify({
        'response': response,
        'session_id': session_id,
        'role': session['role'],
        'difficulty': session.get('difficulty', 'medium'),
        'question_number': current_question_num,
        'total_questions': total_questions
    })

def generate_feedback_summary(session):
    """Generate comprehensive feedback summary"""
    if not session.get('role') or not session.get('questions_asked'):
        return "No interview data available for feedback."
    
    role_data = {
        'engineer': 'Software Engineer',
        'sales': 'Sales Representative',
        'retail': 'Retail Associate'
    }
    
    role_name = role_data.get(session['role'], session['role'])
    feedback_parts = [f"Interview Feedback Summary for {role_name} Position"]
    feedback_parts.append("=" * 50)
    
    total_scores = {'communication': 0, 'technical': 0, 'examples': 0}
    total_overall = 0
    total_responses = 0
    
    # Get all evaluations from conversation history
    for i, qa in enumerate(session['questions_asked'], 1):
        if qa.get('user_response'):
            # Get evaluation from conversation history - match by content
            eval_data = None
            user_response = qa['user_response']
            
            for event in session['conversation_history']:
                if event.get('role') == 'user' and event.get('content') == user_response:
                    eval_data = event.get('eval')
                    break
            
            # If not found, try to evaluate now
            if not eval_data:
                try:
                    eval_data = agent.llm_service.evaluate_answer(qa['question'], user_response, session['role'])
                except:
                    pass
            
            if eval_data:
                scores = eval_data.get('scores', {})
                overall = eval_data.get('overall', 0)
                
                total_scores['communication'] += scores.get('communication', 0)
                total_scores['technical'] += scores.get('technical', 0)
                total_scores['examples'] += scores.get('examples', 0)
                total_overall += overall
                total_responses += 1
                
                feedback_parts.append(f"\nQuestion {i}: {qa['question'][:70]}")
                feedback_parts.append(f"  Communication: {scores.get('communication', 0)}/5")
                feedback_parts.append(f"  Technical: {scores.get('technical', 0)}/5")
                feedback_parts.append(f"  Examples: {scores.get('examples', 0)}/5")
                feedback_parts.append(f"  Overall: {overall}/100")
                
                if eval_data.get('feedback') and len(eval_data['feedback']) > 0:
                    feedback_parts.append("  Feedback:")
                    for fb in eval_data['feedback']:
                        feedback_parts.append(f"    • {fb}")
    
    if total_responses > 0:
        avg_scores = {k: v / total_responses for k, v in total_scores.items()}
        avg_overall = total_overall / total_responses
        
        feedback_parts.append(f"\n{'=' * 50}")
        feedback_parts.append("Overall Performance:")
        feedback_parts.append(f"  Communication: {avg_scores['communication']:.1f}/5")
        feedback_parts.append(f"  Technical: {avg_scores['technical']:.1f}/5")
        feedback_parts.append(f"  Examples: {avg_scores['examples']:.1f}/5")
        feedback_parts.append(f"  Overall Score: {avg_overall:.1f}/100")
        feedback_parts.append(f"  Questions Answered: {total_responses}/10")
        
        # Add performance assessment
        if avg_overall >= 80:
            feedback_parts.append("\nExcellent performance! You're well-prepared for this role.")
        elif avg_overall >= 60:
            feedback_parts.append("\nGood performance! Continue practicing to improve further.")
        else:
            feedback_parts.append("\nKeep practicing! Focus on providing detailed examples and staying relevant to the role.")
        
        feedback_parts.append("\nTips for improvement:")
        feedback_parts.append("  • Use the STAR method (Situation, Task, Action, Result) for behavioral questions")
        feedback_parts.append("  • Provide specific examples from your experience")
        feedback_parts.append("  • Stay relevant to the role you're applying for")
        feedback_parts.append("  • Practice active listening and ask clarifying questions")
    else:
        feedback_parts.append("\nNo answers were evaluated. Please complete some interview questions first.")
    
    return "\n".join(feedback_parts)

@app.route('/api/reset', methods=['POST'])
def reset():
    data = request.json
    session_id = data.get('session_id', 'default')
    if session_id in interview_sessions:
        # Save before deleting
        save_session(session_id, interview_sessions[session_id])
        del interview_sessions[session_id]
    return jsonify({'status': 'reset'})

@app.route('/api/session/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get session data"""
    session_file = DATA_DIR / f"{session_id}.json"
    if session_file.exists():
        with open(session_file, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    return jsonify({'error': 'Session not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
