"""
AI integration module for Invoice Resolver.

Provides dispute letter drafting using OpenAI GPT-4 or Anthropic Claude.
"""

from .dispute_drafter import DisputeLetterGenerator, draft_dispute_letter

__all__ = ["DisputeLetterGenerator", "draft_dispute_letter"]
