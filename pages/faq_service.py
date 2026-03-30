"""
FAQ Service for AI-assisted suggestion generation.

This service integrates with AI providers to generate FAQ suggestions based on user messages.
Currently provides a placeholder implementation that can be extended with real AI services.

Supported providers:
- OpenAI GPT
- Hugging Face
- Local rule-based system
"""

import os
from typing import List, Dict
import random


class FAQService:
    """Service for generating FAQ suggestions"""

    # Sample FAQ database - in production, this would come from a database
    SAMPLE_FAQS = [
        {
            'category': 'hours',
            'content': 'Our organization is open Monday through Friday, 9:00 AM to 5:00 PM. We also have extended hours on weekends for special events.',
            'keywords': ['hours', 'time', 'when', 'open', 'schedule'],
        },
        {
            'category': 'location',
            'content': 'We are located at 123 Main Street, Downtown. Parking is available in the adjacent lot.',
            'keywords': ['location', 'address', 'where', 'place'],
        },
        {
            'category': 'volunteer_requirements',
            'content': 'Volunteers must be at least 18 years old and pass a background check. Training is provided.',
            'keywords': ['requirement', 'age', 'qualification', 'background', 'training'],
        },
        {
            'category': 'contact',
            'content': 'You can reach us at (555) 123-4567 or email us at info@organization.org',
            'keywords': ['contact', 'phone', 'email', 'reach', 'get in touch'],
        },
        {
            'category': 'benefits',
            'content': 'Volunteers receive free training, networking opportunities, and a certificate of service.',
            'keywords': ['benefit', 'offer', 'reward', 'advantage', 'perk'],
        },
    ]

    @classmethod
    def generate_suggestions(cls, message_content: str, num_suggestions: int = 3) -> List[Dict]:
        """
        Generate FAQ suggestions based on user message.
        
        Args:
            message_content: The user's message to analyze
            num_suggestions: Number of suggestions to return
            
        Returns:
            List of suggested FAQs with relevance scores
        """
        # Use OpenAI if configured
        if cls._has_openai_key():
            return cls._generate_with_openai(message_content, num_suggestions)
        
        # Fall back to rule-based matching
        return cls._generate_with_rule_based(message_content, num_suggestions)

    @classmethod
    def _has_openai_key(cls) -> bool:
        """Check if OpenAI API key is configured"""
        return bool(os.getenv('OPENAI_API_KEY'))

    @classmethod
    def _generate_with_openai(cls, message_content: str, num_suggestions: int) -> List[Dict]:
        """Generate suggestions using OpenAI GPT"""
        try:
            import openai
            openai.api_key = os.getenv('OPENAI_API_KEY')

            prompt = f"""
            Based on the following volunteer question, suggest relevant FAQ responses from our database.
            Return {num_suggestions} of the most relevant FAQs in JSON format.
            
            Question: {message_content}
            
            For each suggestion, provide:
            - faq_content: The FAQ text
            - relevance_score: A score from 0 to 1 indicating how relevant it is
            
            Return response as a JSON array.
            """

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500,
            )

            # Parse and return response
            import json
            suggestions = json.loads(response.choices[0].message.content)
            return suggestions

        except Exception as e:
            print(f"Error with OpenAI: {e}")
            # Fall back to rule-based
            return cls._generate_with_rule_based(message_content, num_suggestions)

    @classmethod
    def _generate_with_rule_based(cls, message_content: str, num_suggestions: int) -> List[Dict]:
        """Generate suggestions using rule-based keyword matching"""
        message_lower = message_content.lower()
        
        # Score each FAQ based on keyword matches
        scored_faqs = []
        for faq in cls.SAMPLE_FAQS:
            matched_keywords = sum(
                1 for keyword in faq['keywords']
                if keyword.lower() in message_lower
            )
            score = matched_keywords / len(faq['keywords']) if faq['keywords'] else 0
            
            scored_faqs.append({
                'faq_content': faq['content'],
                'relevance_score': min(score, 1.0),  # Cap at 1.0
            })
        
        # Sort by relevance (descending)
        scored_faqs.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # If no FAQs matched keywords, return all FAQs with zero relevance
        # to ensure we always have suggestions to return
        if not any(faq['relevance_score'] > 0 for faq in scored_faqs):
            # When no keywords match, return all FAQs with relevance 0
            # This ensures empty messages still get suggestions
            for faq in scored_faqs:
                faq['relevance_score'] = 0.1  # Small relevance for default suggestions
            scored_faqs.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Return top N (or all if fewer than N)
        return scored_faqs[:num_suggestions]

    @classmethod
    def add_custom_faq(cls, content: str, keywords: List[str], category: str = 'custom') -> None:
        """
        Add a custom FAQ to the suggestion database.
        In production, this would save to the database.
        
        Args:
            content: The FAQ content
            keywords: List of keywords for matching
            category: The FAQ category
        """
        faq = {
            'category': category,
            'content': content,
            'keywords': keywords,
        }
        cls.SAMPLE_FAQS.append(faq)


def get_suggestions(message_content: str, num_suggestions: int = 3) -> List[Dict]:
    """
    Convenience function to get FAQ suggestions.
    
    Args:
        message_content: The user's message
        num_suggestions: Number of suggestions to return
        
    Returns:
        List of FAQ suggestions with relevance scores
    """
    return FAQService.generate_suggestions(message_content, num_suggestions)
