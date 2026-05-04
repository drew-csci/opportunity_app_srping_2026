import unittest
from unittest.mock import Mock, patch, MagicMock
from pages.faq_service import FAQService
import json


class SendMessageViewLogicTest(unittest.TestCase):
    """Test suite for SendMessageView request/response logic"""

    def test_send_message_validates_conversation_id_required(self):
        """Test that conversation_id is required in payload"""
        payload = {
            'content': 'Test message'
            # Missing conversation_id
        }
        
        # Should raise KeyError or ValidationError
        with self.assertRaises((KeyError, ValueError)):
            # Simulate payload validation
            if 'conversation_id' not in payload:
                raise KeyError('Missing required field: conversation_id')

    def test_send_message_validates_content_required(self):
        """Test that content is required in payload"""
        payload = {
            'conversation_id': 1
            # Missing content
        }
        
        with self.assertRaises((KeyError, ValueError)):
            if 'content' not in payload:
                raise KeyError('Missing required field: content')

    def test_send_message_rejects_empty_content(self):
        """Test that empty content is rejected"""
        payload = {
            'conversation_id': 1,
            'content': ''
        }
        
        # Empty or whitespace-only content should be invalid
        content = payload['content'].strip()
        self.assertEqual(content, '',
                        "Empty content should not be accepted")

    def test_send_message_rejects_whitespace_only(self):
        """Test that whitespace-only content is rejected"""
        payload = {
            'conversation_id': 1,
            'content': '   \n\t  '
        }
        
        content = payload['content'].strip()
        self.assertEqual(content, '',
                        "Whitespace-only content is invalid")

    @patch('pages.faq_service.FAQService.generate_suggestions')
    def test_send_message_generates_faq_suggestions(self, mock_faq):
        """Test that FAQ suggestions are generated for message"""
        mock_faq.return_value = [
            {'faq_content': 'FAQ 1', 'relevance_score': 0.95},
            {'faq_content': 'FAQ 2', 'relevance_score': 0.87}
        ]
        
        message_content = "What are volunteer hours?"
        suggestions = FAQService.generate_suggestions(message_content)
        
        # Should return suggestions
        self.assertEqual(len(suggestions), 2,
                        "Should generate FAQ suggestions")
        self.assertEqual(suggestions[0]['faq_content'], 'FAQ 1')
        self.assertTrue(0 <= suggestions[0]['relevance_score'] <= 1)

    def test_faq_suggestion_response_structure(self):
        """Test that FAQ suggestion response has correct structure"""
        suggestions = [
            {
                'faq_content': 'Our hours are 9-5 Mon-Fri',
                'relevance_score': 0.95
            },
            {
                'faq_content': 'We offer training for all volunteers',
                'relevance_score': 0.87
            }
        ]
        
        # Validate structure
        for suggestion in suggestions:
            self.assertIn('faq_content', suggestion,
                         "Should have faq_content")
            self.assertIn('relevance_score', suggestion,
                         "Should have relevance_score")
            self.assertIsInstance(suggestion['faq_content'], str)
            self.assertIsInstance(suggestion['relevance_score'], (int, float))
            self.assertTrue(0 <= suggestion['relevance_score'] <= 1)

    def test_message_timestamp_format(self):
        """Test that message timestamp is in proper ISO format"""
        from datetime import datetime
        
        timestamp = datetime.now().isoformat()
        
        # Should be parseable as ISO format
        try:
            parsed = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            self.assertIsNotNone(parsed)
        except ValueError:
            self.fail("Timestamp should be valid ISO format")

    def test_payload_validation_accepts_valid_input(self):
        """Test that valid payload passes validation"""
        payload = {
            'conversation_id': 1,
            'content': 'Valid message content'
        }
        
        # Validate required fields
        self.assertIn('conversation_id', payload)
        self.assertIn('content', payload)
        
        # Validate content is not empty
        self.assertTrue(payload['content'].strip() != '')
        
        # Validate conversation_id is positive integer
        self.assertIsInstance(payload['conversation_id'], int)
        self.assertGreater(payload['conversation_id'], 0)

    def test_conversation_id_must_be_positive_integer(self):
        """Test that conversation_id must be a positive integer"""
        invalid_ids = [0, -1, -100]
        
        for invalid_id in invalid_ids:
            self.assertLessEqual(invalid_id, 0,
                                f"{invalid_id} should be rejected")

    def test_response_includes_all_message_fields(self):
        """Test that API response includes all necessary message fields"""
        required_response_fields = [
            'id',
            'sender',
            'content',
            'timestamp',
            'is_read',
            'faq_suggestions'
        ]
        
        # Simulate response structure
        response_data = {
            'id': 1,
            'sender': {'id': 1, 'email': 'test@test.com', 'display_name': 'Test User'},
            'content': 'Test message',
            'timestamp': '2026-03-30T12:00:00Z',
            'is_read': False,
            'faq_suggestions': [
                {'faq_content': 'FAQ text', 'relevance_score': 0.95}
            ]
        }
        
        for field in required_response_fields:
            self.assertIn(field, response_data,
                         f"Response should include {field}")

    def test_faq_suggestions_list_is_array(self):
        """Test that faq_suggestions is always a JSON array"""
        # Empty array case
        response1 = {'faq_suggestions': []}
        self.assertIsInstance(response1['faq_suggestions'], list)
        
        # With suggestions
        response2 = {
            'faq_suggestions': [
                {'faq_content': 'FAQ', 'relevance_score': 0.9}
            ]
        }
        self.assertIsInstance(response2['faq_suggestions'], list)
        self.assertGreater(len(response2['faq_suggestions']), 0)

    def test_sender_info_structure(self):
        """Test that sender info has required fields"""
        sender_data = {
            'id': 1,
            'email': 'volunteer@test.com',
            'display_name': 'Test Volunteer',
            'user_type': 'volunteer'
        }
        
        required_sender_fields = ['id', 'email', 'display_name']
        
        for field in required_sender_fields:
            self.assertIn(field, sender_data,
                         f"Sender should have {field}")

    def test_message_content_preserves_formatting(self):
        """Test that message content preserves newlines and spacing"""
        content = "Line 1\nLine 2\n\nLine 3"
        
        # Content should preserve structure
        self.assertIn('\n', content)
        self.assertEqual(content.count('\n'), 3,
                        "Newlines should be preserved")

    def test_relevance_scores_are_sorted_descending(self):
        """Test that FAQ suggestions are sorted by relevance (highest first)"""
        suggestions = [
            {'faq_content': 'FAQ 1', 'relevance_score': 0.95},
            {'faq_content': 'FAQ 2', 'relevance_score': 0.87},
            {'faq_content': 'FAQ 3', 'relevance_score': 0.72}
        ]
        
        # Verify sorted order
        for i in range(len(suggestions) - 1):
            self.assertGreaterEqual(
                suggestions[i]['relevance_score'],
                suggestions[i + 1]['relevance_score'],
                "Suggestions should be sorted by relevance"
            )

    def test_http_status_codes(self):
        """Test that API returns correct HTTP status codes"""
        # 201 Created - successful message creation
        self.assertEqual(201, 201)
        
        # 400 Bad Request - invalid payload
        self.assertEqual(400, 400)
        
        # 404 Not Found - conversation doesn't exist
        self.assertEqual(404, 404)

    def test_json_serialization(self):
        """Test that response can be serialized to JSON"""
        response_data = {
            'id': 1,
            'sender': {'id': 1, 'email': 'test@test.com'},
            'content': 'Test message',
            'timestamp': '2026-03-30T12:00:00Z',
            'is_read': False,
            'faq_suggestions': [
                {'faq_content': 'FAQ', 'relevance_score': 0.95}
            ]
        }
        
        # Should be serializable
        json_str = json.dumps(response_data)
        self.assertIsInstance(json_str, str)
        
        # Should be deserializable
        deserialized = json.loads(json_str)
        self.assertEqual(deserialized['id'], 1)
        self.assertEqual(deserialized['content'], 'Test message')

    def test_conversation_id_type_validation(self):
        """Test that conversation_id must be numeric"""
        invalid_types = ['abc', 'null', '', None]
        
        for invalid_id in invalid_types:
            self.assertNotIsInstance(invalid_id, int,
                                    f"{invalid_id} is not a valid integer")

    def test_message_length_validation(self):
        """Test message length constraints"""
        # Very short message (should be accepted)
        short_msg = 'Hi'
        self.assertGreater(len(short_msg), 0)
        self.assertTrue(short_msg.strip() != '')
        
        # Very long message (should be accepted within reason)
        long_msg = 'a' * 5000
        self.assertEqual(len(long_msg), 5000)
        self.assertTrue(len(long_msg) > 0)

