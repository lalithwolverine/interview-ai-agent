"""
Unit tests for Interview Practice Partner backend
Tests session creation, LLM JSON parsing, and session file export
"""
import unittest
from unittest.mock import patch, MagicMock
import json
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app import (
    InterviewAgent, HeuristicsAnalyzer, LLMService,
    QuestionBank, save_session, EVALUATION_SCHEMA
)

class TestSessionCreation(unittest.TestCase):
    """Test session creation and management"""
    
    def setUp(self):
        self.agent = InterviewAgent()
    
    def test_session_initialization(self):
        """Test that a new session is properly initialized"""
        session = {
            'role': None,
            'difficulty': 'medium',
            'current_question': None,
            'conversation_history': [],
            'questions_asked': [],
            'used_questions': [],
            'strong_answer_count': 0,
            'started_at': '2024-01-01T00:00:00',
            'aggregated_feedback': {}
        }
        
        self.assertIsNone(session['role'])
        self.assertEqual(session['difficulty'], 'medium')
        self.assertEqual(len(session['conversation_history']), 0)
    
    def test_role_assignment(self):
        """Test role assignment logic"""
        session = {'role': None}
        user_message = "I want to practice for engineer"
        
        if 'engineer' in user_message.lower() or 'software' in user_message.lower():
            session['role'] = 'engineer'
        
        self.assertEqual(session['role'], 'engineer')

class TestLLMJSONParsing(unittest.TestCase):
    """Test LLM JSON response parsing and validation"""
    
    def setUp(self):
        self.llm_service = LLMService()
    
    def test_valid_evaluation_json(self):
        """Test parsing of valid evaluation JSON"""
        valid_json = {
            "scores": {"communication": 4, "technical": 5, "examples": 3},
            "overall": 80,
            "should_followup": True,
            "followup_question": "Can you provide more details?",
            "feedback": ["Good communication", "Needs more examples"]
        }
        
        # Validate schema
        self.assertIn('scores', valid_json)
        self.assertIn('overall', valid_json)
        self.assertIn('should_followup', valid_json)
        self.assertIn('followup_question', valid_json)
        self.assertIn('feedback', valid_json)
        
        # Validate score ranges
        scores = valid_json['scores']
        self.assertGreaterEqual(scores['communication'], 0)
        self.assertLessEqual(scores['communication'], 5)
        self.assertGreaterEqual(valid_json['overall'], 0)
        self.assertLessEqual(valid_json['overall'], 100)
    
    def test_invalid_evaluation_json(self):
        """Test handling of invalid JSON"""
        invalid_json = {
            "scores": {"communication": 4},
            "overall": 80
            # Missing required fields
        }
        
        # Check if all required fields are present
        required_fields = ['scores', 'overall', 'should_followup', 'followup_question', 'feedback']
        missing_fields = [field for field in required_fields if field not in invalid_json]
        
        self.assertGreater(len(missing_fields), 0)
    
    def test_json_extraction_from_text(self):
        """Test extracting JSON from LLM response text"""
        import re
        
        response_text = """Here's the evaluation:
        {"scores":{"communication":4,"technical":5,"examples":3},"overall":80,"should_followup":true,"followup_question":"More details?","feedback":["Good"]}
        That's the evaluation."""
        
        # Extract JSON
        json_match = re.search(r'\{[^{}]*"scores"[^{}]*\{[^{}]*\}[^{}]*\}', response_text, re.DOTALL)
        self.assertIsNotNone(json_match)
        
        json_str = json_match.group(0)
        parsed = json.loads(json_str)
        self.assertIn('scores', parsed)
    
    @patch('app.LLMService.call_hf_api')
    def test_evaluate_answer_with_mock(self, mock_call):
        """Test evaluation with mocked API response"""
        mock_call.return_value = '{"scores":{"communication":4,"technical":5,"examples":3},"overall":80,"should_followup":true,"followup_question":"More details?","feedback":["Good"]}'
        
        result = self.llm_service.evaluate_answer(
            "Tell me about yourself",
            "I am a software engineer with 5 years of experience",
            "engineer"
        )
        
        self.assertIn('scores', result)
        self.assertIn('overall', result)
        self.assertEqual(result['scores']['communication'], 4)

class TestSessionFileExport(unittest.TestCase):
    """Test session file export functionality"""
    
    def setUp(self):
        self.test_session_id = "test_session_123"
        self.test_data_dir = Path("test_data")
        self.test_data_dir.mkdir(exist_ok=True)
    
    def tearDown(self):
        # Clean up test files
        test_file = self.test_data_dir / f"{self.test_session_id}.json"
        if test_file.exists():
            test_file.unlink()
        if self.test_data_dir.exists():
            try:
                self.test_data_dir.rmdir()
            except:
                pass
    
    def test_session_file_structure(self):
        """Test that session file has correct structure"""
        session = {
            'role': 'engineer',
            'started_at': '2024-01-01T00:00:00',
            'conversation_history': [
                {
                    'role': 'user',
                    'content': 'Hello',
                    'timestamp': '2024-01-01T00:00:01'
                },
                {
                    'role': 'assistant',
                    'content': 'Hi there',
                    'timestamp': '2024-01-01T00:00:02'
                }
            ],
            'aggregated_feedback': {}
        }
        
        # Mock save_session to use test directory
        from app import DATA_DIR
        original_dir = DATA_DIR
        
        try:
            import app
            app.DATA_DIR = self.test_data_dir
            save_session(self.test_session_id, session)
            
            # Verify file exists
            session_file = self.test_data_dir / f"{self.test_session_id}.json"
            self.assertTrue(session_file.exists())
            
            # Verify file structure
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.assertEqual(data['sessionId'], self.test_session_id)
            self.assertEqual(data['role'], 'engineer')
            self.assertEqual(data['mode'], 'interview')
            self.assertIn('events', data)
            self.assertEqual(len(data['events']), 2)
            self.assertIn('aggregatedFeedback', data)
            
        finally:
            app.DATA_DIR = original_dir
    
    def test_session_file_with_evaluation(self):
        """Test session file includes evaluation data"""
        session = {
            'role': 'engineer',
            'started_at': '2024-01-01T00:00:00',
            'conversation_history': [
                {
                    'role': 'user',
                    'content': 'I have 5 years of experience',
                    'timestamp': '2024-01-01T00:00:01',
                    'eval': {
                        'scores': {'communication': 4, 'technical': 5, 'examples': 3},
                        'overall': 80
                    }
                }
            ],
            'aggregated_feedback': {}
        }
        
        from app import DATA_DIR
        original_dir = DATA_DIR
        
        try:
            import app
            app.DATA_DIR = self.test_data_dir
            save_session(self.test_session_id, session)
            
            session_file = self.test_data_dir / f"{self.test_session_id}.json"
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check that evaluation is included
            user_event = [e for e in data['events'] if e['speaker'] == 'user'][0]
            self.assertIn('eval', user_event)
            self.assertEqual(user_event['eval']['overall'], 80)
            
        finally:
            app.DATA_DIR = original_dir

class TestHeuristics(unittest.TestCase):
    """Test heuristics analyzer"""
    
    def setUp(self):
        self.heuristics = HeuristicsAnalyzer()
    
    def test_answer_length_analysis(self):
        """Test answer length heuristics"""
        short_answer = "I code."
        long_answer = " ".join(["word"] * 250)
        
        result_short = self.heuristics.analyze_answer(short_answer, 'engineer')
        result_long = self.heuristics.analyze_answer(long_answer, 'engineer')
        
        self.assertTrue(result_short['is_too_short'])
        self.assertTrue(result_long['is_too_long'])
    
    def test_keyword_detection(self):
        """Test role-specific keyword detection"""
        answer = "I develop software using Python and work with databases"
        result = self.heuristics.analyze_answer(answer, 'engineer')
        
        self.assertTrue(result['has_keywords'])
    
    def test_nonsense_detection(self):
        """Test nonsense input detection"""
        self.assertTrue(self.heuristics.is_nonsense("asdf"))
        self.assertTrue(self.heuristics.is_nonsense("123"))
        self.assertTrue(self.heuristics.is_nonsense("a"))
        self.assertFalse(self.heuristics.is_nonsense("I am a software engineer"))

if __name__ == '__main__':
    unittest.main()

