import unittest
from pages.faq_service import FAQService


class FAQServiceSuggestionGenerationTest(unittest.TestCase):
    """Test suite for FAQService.generate_suggestions()"""

    def test_generate_suggestions_returns_three_results(self):
        """Test that generate_suggestions returns exactly 3 suggestions by default"""
        service = FAQService()
        suggestions = service.generate_suggestions("What are your volunteer hours?")
        self.assertEqual(len(suggestions), 3,
                        "Should return exactly 3 suggestions by default")

    def test_generate_suggestions_ranked_by_relevance(self):
        """Test that suggestions are ranked by relevance score (highest to lowest)"""
        service = FAQService()
        suggestions = service.generate_suggestions("What are your hours?")
        
        # Verify scores are in descending order
        for i in range(len(suggestions) - 1):
            self.assertGreaterEqual(
                suggestions[i]['relevance_score'],
                suggestions[i + 1]['relevance_score'],
                "Suggestions should be ordered by relevance score (highest first)"
            )

    def test_relevance_scores_in_valid_range(self):
        """Test that all relevance scores are between 0.0 and 1.0"""
        service = FAQService()
        suggestions = service.generate_suggestions("What are volunteer requirements?")
        
        for suggestion in suggestions:
            self.assertGreaterEqual(
                suggestion['relevance_score'], 0.0,
                "Relevance score should be >= 0.0"
            )
            self.assertLessEqual(
                suggestion['relevance_score'], 1.0,
                "Relevance score should be <= 1.0"
            )

    def test_suggestions_have_faq_content(self):
        """Test that each suggestion has faq_content field with valid content"""
        service = FAQService()
        suggestions = service.generate_suggestions("Tell me about your hours")
        
        for suggestion in suggestions:
            self.assertIn('faq_content', suggestion,
                         "Each suggestion must have 'faq_content' field")
            self.assertIsNotNone(suggestion['faq_content'],
                               "faq_content cannot be None")
            self.assertTrue(len(suggestion['faq_content']) > 0,
                           "faq_content must be non-empty string")

    def test_empty_message_returns_suggestions(self):
        """Test that empty message content still returns suggestions"""
        service = FAQService()
        suggestions = service.generate_suggestions("")
        
        # Should return default FAQs even with empty input
        self.assertEqual(len(suggestions), 3,
                        "Should return 3 suggestions even for empty message")
        self.assertTrue(
            all('relevance_score' in s for s in suggestions),
            "All suggestions should have relevance_score"
        )

    def test_custom_num_suggestions_parameter(self):
        """Test that num_suggestions parameter is respected"""
        service = FAQService()
        
        suggestions_1 = service.generate_suggestions(
            "What are the hours?", 
            num_suggestions=1
        )
        suggestions_2 = service.generate_suggestions(
            "What are the hours?", 
            num_suggestions=2
        )
        suggestions_5 = service.generate_suggestions(
            "What are the hours?", 
            num_suggestions=5
        )
        
        self.assertEqual(len(suggestions_1), 1,
                        "Should return 1 suggestion when requested")
        self.assertEqual(len(suggestions_2), 2,
                        "Should return 2 suggestions when requested")
        self.assertLessEqual(len(suggestions_5), 5,
                            "Should return up to 5 suggestions")

    def test_high_relevance_for_exact_keywords(self):
        """Test that exact keyword matches have higher relevance scores"""
        service = FAQService()
        
        # Message with exact keyword match should have highest relevance
        exact_match = service.generate_suggestions("What are your hours?")
        vague_message = service.generate_suggestions("Tell me something")
        
        # First suggestion of exact match should have higher relevance
        # than first suggestion of vague message
        self.assertGreater(
            exact_match[0]['relevance_score'],
            vague_message[0]['relevance_score'],
            "Exact keyword match should have higher relevance than vague query"
        )

    def test_suggestions_are_unique(self):
        """Test that returned suggestions are unique (no duplicates)"""
        service = FAQService()
        suggestions = service.generate_suggestions(
            "volunteer hours schedule availability"
        )
        
        # Extract FAQ content to check uniqueness
        faq_contents = [s['faq_content'] for s in suggestions]
        unique_contents = set(faq_contents)
        
        self.assertEqual(len(faq_contents), len(unique_contents),
                        "All suggestions should be unique, no duplicates")

    def test_suggestions_have_required_fields(self):
        """Test that each suggestion has all required fields"""
        service = FAQService()
        suggestions = service.generate_suggestions("What can I do here?")
        
        required_fields = ['faq_content', 'relevance_score']
        
        for index, suggestion in enumerate(suggestions):
            for field in required_fields:
                self.assertIn(field, suggestion,
                             f"Suggestion {index} missing required field: {field}")

    def test_different_queries_produce_different_rankings(self):
        """Test that different queries produce different suggestion rankings"""
        service = FAQService()
        
        hours_suggestions = service.generate_suggestions("What are your hours?")
        location_suggestions = service.generate_suggestions("Where are you located?")
        
        # At least one suggestion should be ranked differently
        hours_top_faq = hours_suggestions[0]['faq_content']
        location_top_faq = location_suggestions[0]['faq_content']
        
        # They might be the same FAQ, but with different relevance scores
        # OR they could be completely different FAQs
        # This test verifies the service is actually comparing content
        self.assertTrue(
            hours_top_faq != location_top_faq or 
            hours_suggestions[0]['relevance_score'] != location_suggestions[0]['relevance_score'],
            "Different queries should produce different suggestion rankings"
        )

    def test_message_with_multiple_keywords(self):
        """Test that message with multiple relevant keywords has reasonable relevance"""
        service = FAQService()
        
        # Message with multiple keywords should have decent relevance
        multi_keyword = service.generate_suggestions(
            "What are your volunteer hours and schedule availability?"
        )
        
        # With 2 matching keywords out of 5 in the hours FAQ, we should get 0.4 relevance
        # This is >= 0.2 which shows keywords are being matched
        self.assertGreater(
            multi_keyword[0]['relevance_score'],
            0.2,
            "Message with multiple keywords should score > 0.2 relevance"
        )
