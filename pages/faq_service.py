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
            'category': 'opportunities',
            'content': 'We offer various volunteering opportunities including tutoring, community service, environmental projects, and skill-building workshops. Check our dashboard for current openings.',
            'keywords': ['opportunities', 'volunteer', 'jobs', 'positions', 'available'],
        },
        {
            'category': 'requirements',
            'content': 'Most opportunities require students to be enrolled in high school or university. Some roles may have age restrictions or require background checks. Check individual opportunity descriptions for specific requirements.',
            'keywords': ['requirements', 'qualifications', 'eligible', 'age', 'background'],
        },
        {
            'category': 'application',
            'content': 'To apply for an opportunity, create an account, browse available positions, and submit your application through the platform. Organizations will review and contact you directly.',
            'keywords': ['apply', 'application', 'how to', 'submit', 'process'],
        },
        {
            'category': 'contact',
            'content': 'You can contact organizations directly through our messaging system once you apply. For platform support, email support@opportunityapp.org.',
            'keywords': ['contact', 'reach', 'email', 'support', 'help'],
        },
        {
            'category': 'benefits',
            'content': 'Volunteering helps build your resume, develop new skills, network with professionals, and contribute to your community. Many opportunities provide certificates of completion.',
            'keywords': ['benefits', 'why', 'advantages', 'resume', 'skills'],
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
            from openai import OpenAI
            import json

            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

            prompt = f"""
            Based on the following volunteer question, suggest relevant FAQ responses from our database.
            Return {num_suggestions} of the most relevant FAQs in JSON format.
            
            Question: {message_content}
            
            For each suggestion, provide:
            - faq_content: The FAQ text
            - relevance_score: A score from 0 to 1 indicating how relevant it is
            
            Return response as a JSON array.
            """

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500,
            )

            # Parse and return response, ensuring we only return num_suggestions
            suggestions = json.loads(response.choices[0].message.content)
            # Ensure we respect the num_suggestions limit
            return suggestions[:num_suggestions] if len(suggestions) > num_suggestions else suggestions

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
        # Explicitly limit to num_suggestions
        result = scored_faqs[:num_suggestions]
        return result if len(result) > 0 else scored_faqs[:1]

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
