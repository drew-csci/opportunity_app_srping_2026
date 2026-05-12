import unittest
from unittest.mock import Mock, patch
import json
from datetime import datetime
from pages.faq_service import FAQService


class MessageCreationAndFAQGenerationIntegrationTest(unittest.TestCase):
    """
    Integration test for the complete message creation and FAQ generation flow.
    
    This test validates the entire happy path without requiring database:
    1. Setup: Create mock users and conversation
    2. Action: Simulate sending message via API
    3. Verification: Verify complete message object and FAQ generation
    """

    def setUp(self):
        """Set up test fixtures with mocked objects"""
        
        # Mock user objects
        self.volunteer = Mock()
        self.volunteer.id = 1
        self.volunteer.email = 'volunteer@test.com'
        self.volunteer.display_name = 'Test Volunteer'
        self.volunteer.user_type = 'volunteer'
        
        self.organization = Mock()
        self.organization.id = 2
        self.organization.email = 'org@test.com'
        self.organization.display_name = 'Test Organization'
        self.organization.user_type = 'organization'
        
        # Mock conversation object
        self.conversation = Mock()
        self.conversation.id = 1
        self.conversation.volunteer = self.volunteer
        self.conversation.organization = self.organization
        self.conversation.created_at = datetime.now()
        self.conversation.last_message_at = datetime.now()

    def test_message_creation_and_faq_generation_complete_flow(self):
        """
        INTEGRATION TEST: Complete message creation and FAQ generation flow
        
        Simulates the entire happy path:
        1. Send message via API (simulated)
        2. Generate FAQ suggestions
        3. Create response object
        4. Verify all data integrity
        """
        
        print("\n" + "="*70)
        print("INTEGRATION TEST: Message Creation and FAQ Generation")
        print("="*70)
        
        # STEP 1: Simulate sending message
        message_content = "What are your volunteer hours and requirements?"
        
        # Create mock message object
        message = Mock()
        message.id = 100
        message.conversation = self.conversation
        message.sender = self.volunteer
        message.content = message_content
        message.timestamp = datetime.now()
        message.is_read = False
        
        print(f"\n[OK] Step 1: Message created")
        print(f"  - ID: {message.id}")
        print(f"  - Content: {message.content}")
        print(f"  - Sender: {message.sender.display_name}")
        
        # STEP 2: Generate FAQ suggestions (actual call)
        faq_suggestions = FAQService.generate_suggestions(message_content)
        
        self.assertGreater(len(faq_suggestions), 0,
                          "FAQ suggestions should be generated")
        self.assertLessEqual(len(faq_suggestions), 3,
                            "Should generate at most 3 suggestions")
        
        print(f"\n[OK] Step 2: FAQ suggestions generated")
        print(f"  - Count: {len(faq_suggestions)}")
        
        for i, faq in enumerate(faq_suggestions):
            self.assertIn('faq_content', faq)
            self.assertIn('relevance_score', faq)
            self.assertEqual(len(faq['faq_content']) > 0, True)
            self.assertTrue(0.0 <= faq['relevance_score'] <= 1.0)
            print(f"  - Suggestion {i+1}: {faq['relevance_score']:.2%}")
        
        # STEP 3: Create response object
        response_data = {
            'id': message.id,
            'sender': {
                'id': message.sender.id,
                'email': message.sender.email,
                'display_name': message.sender.display_name
            },
            'content': message.content,
            'timestamp': message.timestamp.isoformat(),
            'is_read': message.is_read,
            'faq_suggestions': faq_suggestions
        }
        
        print(f"\n[OK] Step 3: Response object created")
        print(f"  - Fields: {list(response_data.keys())}")
        
        # STEP 4: Verify JSON serialization
        response_json = json.dumps(response_data)
        self.assertIsInstance(response_json, str)
        
        deserialized = json.loads(response_json)
        self.assertEqual(deserialized['id'], message.id)
        self.assertEqual(deserialized['content'], message_content)
        
        print(f"\n[OK] Step 4: Response serializable to JSON")
        print(f"  - Size: {len(response_json)} bytes")
        
        # STEP 5: Verify message state
        self.assertEqual(message.conversation.id, self.conversation.id)
        self.assertIsNotNone(message.sender)
        self.assertGreater(len(message.content), 0)
        self.assertFalse(message.is_read)
        
        print(f"\n[OK] Step 5: Message state verified")
        print(f"  - Conversation linked: [OK]")
        print(f"  - Sender assigned: [OK]")
        print(f"  - is_read = False: [OK]")
        
        print("\n" + "="*70)
        print("[PASS] INTEGRATION TEST PASSED")
        print("="*70 + "\n")

    def test_message_with_keywords_gets_relevant_faqs(self):
        """
        INTEGRATION TEST: Keywords in message get matched FAQs
        """
        
        print("\n" + "="*70)
        print("INTEGRATION TEST: Keyword Matching in FAQ Generation")
        print("="*70 + "\n")
        
        message_content = "What are your volunteer hours and availability schedule?"
        faq_suggestions = FAQService.generate_suggestions(message_content)
        
        self.assertGreater(len(faq_suggestions), 0)
        self.assertGreater(faq_suggestions[0]['relevance_score'], 0.0)
        
        print(f"[OK] Message: {message_content}")
        print(f"[OK] Generated {len(faq_suggestions)} suggestions")
        print(f"[OK] Top relevance: {faq_suggestions[0]['relevance_score']:.2%}")
        print("\n[PASS] INTEGRATION TEST PASSED\n")

    def test_multiple_messages_different_faqs(self):
        """
        INTEGRATION TEST: Different messages generate different FAQs
        """
        
        print("\n" + "="*70)
        print("INTEGRATION TEST: Different Messages Different FAQs")
        print("="*70 + "\n")
        
        msg1_content = "What are your volunteer hours?"
        faqs1 = FAQService.generate_suggestions(msg1_content)
        
        msg2_content = "What are the volunteer requirements?"
        faqs2 = FAQService.generate_suggestions(msg2_content)
        
        self.assertGreater(len(faqs1), 0)
        self.assertGreater(len(faqs2), 0)
        
        different = (
            faqs1[0]['faq_content'] != faqs2[0]['faq_content'] or
            faqs1[0]['relevance_score'] != faqs2[0]['relevance_score']
        )
        self.assertTrue(different)
        
        print(f"[OK] Message 1: {msg1_content}")
        print(f"  Top FAQ relevance: {faqs1[0]['relevance_score']:.2%}")
        print(f"\n[OK] Message 2: {msg2_content}")
        print(f"  Top FAQ relevance: {faqs2[0]['relevance_score']:.2%}")
        print(f"\n[OK] Rankings differ based on content")
        print("\n[PASS] INTEGRATION TEST PASSED\n")

    def test_faq_suggestions_ranked_by_relevance(self):
        """
        INTEGRATION TEST: FAQ suggestions ranked by relevance
        """
        
        print("\n" + "="*70)
        print("INTEGRATION TEST: FAQ Suggestion Ranking")
        print("="*70 + "\n")
        
        message_content = "volunteer hours schedule availability"
        faqs = FAQService.generate_suggestions(message_content)
        
        print(f"[OK] Message: {message_content}\n")
        
        for i in range(len(faqs) - 1):
            self.assertGreaterEqual(
                faqs[i]['relevance_score'],
                faqs[i + 1]['relevance_score']
            )
        
        for i, faq in enumerate(faqs):
            print(f"  {i+1}. [{faq['relevance_score']:.2%}] {faq['faq_content'][:50]}...")
        
        print(f"\n[OK] Properly ranked (highest first)")
        print("\n[PASS] INTEGRATION TEST PASSED\n")

    def test_response_json_valid_and_parseable(self):
        """
        INTEGRATION TEST: API response is valid, parseable JSON
        """
        
        print("\n" + "="*70)
        print("INTEGRATION TEST: JSON Response Validity")
        print("="*70 + "\n")
        
        message_id = 100
        faqs = FAQService.generate_suggestions("What are your hours?")
        
        response_data = {
            'id': message_id,
            'sender': {
                'id': 1,
                'email': 'volunteer@test.com',
                'display_name': 'Test Volunteer'
            },
            'content': 'What are your hours?',
            'timestamp': datetime.now().isoformat(),
            'is_read': False,
            'faq_suggestions': faqs
        }
        
        # Serialize and deserialize
        json_string = json.dumps(response_data)
        deserialized = json.loads(json_string)
        
        print(f"[OK] Serialized to JSON: {len(json_string)} bytes")
        print(f"[OK] Deserialized successfully")
        print(f"  - Message ID: {deserialized['id']}")
        print(f"  - FAQ count: {len(deserialized['faq_suggestions'])}")
        
        # Verify fields
        required_fields = ['id', 'sender', 'content', 'timestamp', 'is_read', 'faq_suggestions']
        for field in required_fields:
            self.assertIn(field, deserialized)
        
        print(f"[OK] All required fields present")
        
        # Round-trip
        json_string2 = json.dumps(deserialized)
        deserialized2 = json.loads(json_string2)
        self.assertEqual(deserialized2['id'], deserialized['id'])
        
        print(f"[OK] Round-trip serialization successful")
        print("\n[PASS] INTEGRATION TEST PASSED\n")
