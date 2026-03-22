"""
AI-powered dispute letter drafting for invoice resolution.

This module provides functions to generate formal dispute letters using
OpenAI GPT-4 or Anthropic Claude, incorporating invoice details and
evidence for small claims court.
"""

import json
from typing import Optional, Dict, Any, List
from datetime import datetime

import openai
import anthropic

from src.core.config import settings
from src.models import Invoice


class DisputeLetterGenerator:
    """Generates formal dispute letters for unpaid/disputed invoices."""

    def __init__(self):
        """Initialize AI clients based on available API keys."""
        self.openai_client = None
        self.anthropic_client = None
        self.provider = None

        if settings.openai_api_key:
            self.openai_client = openai.OpenAI(api_key=settings.openai_api_key)
            self.provider = "openai"

        if settings.anthropic_api_key:
            self.anthropic_client = anthropic.Anthropic(
                api_key=settings.anthropic_api_key
            )
            if not self.provider:
                self.provider = "anthropic"

        if not self.provider:
            raise ValueError(
                "No AI provider configured. Set OPENAI_API_KEY or ANTHROPIC_API_KEY."
            )

    def draft_dispute_letter(
        self,
        invoice: Invoice,
        evidence_list: List[Dict[str, Any]],
        letter_type: str = "formal_dispute",
        recipient: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a dispute letter using AI.

        Args:
            invoice: Invoice model instance with all details
            evidence_list: List of evidence dicts with keys:
                - date: str (ISO date)
                - description: str
                - amount: float (optional)
                - type: str (payment, communication, etc.)
            letter_type: Type of letter to generate:
                - "formal_dispute": Formal payment dispute letter
                - "small_claims_prep": Small claims court preparation document
                - "demand_letter": Final demand letter before legal action
            recipient: Optional recipient name (defaults to client_name from invoice)

        Returns:
            Dict with keys:
                - content: str (HTML or LaTeX formatted letter)
                - provider: str (AI provider used)
                - tokens_used: int (total tokens consumed)
                - cost_usd: float (estimated cost)
                - generated_at: str (ISO timestamp)
        """
        if not recipient:
            recipient = invoice.client_name or "Valued Client"

        # Build prompt with invoice details and evidence
        prompt = self._build_prompt(invoice, evidence_list, letter_type, recipient)

        # Call AI provider
        if self.provider == "openai":
            result = self._call_openai(prompt, letter_type)
        else:
            result = self._call_anthropic(prompt, letter_type)

        # Add metadata
        result["generated_at"] = datetime.utcnow().isoformat()
        result["letter_type"] = letter_type

        return result

    def _build_prompt(
        self,
        invoice: Invoice,
        evidence_list: List[Dict[str, Any]],
        letter_type: str,
        recipient: Optional[str] = None,
    ) -> str:
        """Construct a structured prompt for the AI."""
        # Default recipient to client name if not provided
        if recipient is None:
            recipient = invoice.client_name or "Valued Client"

        evidence_text = "\n".join(
            f"- {ev.get('date', 'N/A')}: {ev.get('description', '')}"
            + (f" (${ev.get('amount', 0):.2f})" if ev.get("amount") else "")
            for ev in evidence_list
        )

        invoice_details = f"""
Invoice #: {invoice.invoice_number or "N/A"}
Client: {invoice.client_name}
Amount: ${invoice.amount:.2f} {invoice.currency}
Issue Date: {invoice.issue_date.strftime("%Y-%m-%d") if invoice.issue_date else "N/A"}
Due Date: {invoice.due_date.strftime("%Y-%m-%d") if invoice.due_date else "N/A"}
Status: {invoice.status.upper()}
Description: {invoice.description or "N/A"}
"""

        if letter_type == "formal_dispute":
            instructions = """
Write a formal dispute letter that:
1. Is professional and firm but polite
2. Clearly states the invoice details and amount owed
3. Summarizes the evidence of attempted resolution
4. Demands payment within 14 days (specify exact deadline date)
5. Mentions potential escalation to small claims court if unpaid
6. Includes proper business letter format with sender/recipient info
7. Provides payment methods (link, check, bank transfer)
8. Is 1-2 pages maximum

The letter should be in HTML format with appropriate styling for printing.
"""
        elif letter_type == "small_claims_prep":
            instructions = """
Prepare a small claims court summary document that includes:
1. Case summary (who, what, when, where, how much)
2. Chronological timeline of events
3. List of evidence with dates and descriptions
4. Witness information (if any)
5. Calculation of damages (invoice amount + fees if applicable)
6. Court forms to file (provide template text)
7. Jurisdiction information (based on user's location if available)
8. Tips for presenting the case

Format as a clean, printable document with sections and headings.
"""
        else:  # demand_letter
            instructions = """
Write a final demand letter that:
1. Is urgent and serious in tone
2. States that this is final demand before legal action
3. Gives a strict 7-day deadline for payment
4. Specifies consequences of non-payment (small claims filing)
5. Offers payment plan option if full amount cannot be paid
6. Is concise and direct (1 page maximum)

Use HTML format suitable for email attachment.
"""

        prompt = f"""You are a legal assistant drafting a {letter_type} for an unpaid invoice.

RECIPIENT:
{recipient}

INVOICE DETAILS:
{invoice_details}

EVIDENCE OF COMMUNICATION/PAYMENT ATTEMPTS:
{evidence_text if evidence_text else "No specific evidence provided."}

{instructions}

Return ONLY the HTML content of the letter, no explanations. Include proper HTML structure with inline CSS for professional formatting."""

        return prompt

    def _call_openai(self, prompt: str, letter_type: str) -> Dict[str, Any]:
        """Call OpenAI GPT-4 to generate the letter."""
        response = self.openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {
                    "role": "system",
                    "content": "You are a legal document assistant specializing in debt collection and small claims preparation.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=2000,
        )

        content = response.choices[0].message.content or ""
        usage = response.usage

        # Calculate cost (GPT-4 Turbo: $0.01/1K input, $0.03/1K output as of 2024)
        input_cost = (usage.prompt_tokens / 1000) * 0.01
        output_cost = (usage.completion_tokens / 1000) * 0.03
        total_cost = input_cost + output_cost

        return {
            "content": content,
            "provider": "openai/gpt-4-turbo",
            "tokens_used": usage.total_tokens,
            "cost_usd": round(total_cost, 4),
            "model": "gpt-4-turbo-preview",
        }

    def _call_anthropic(self, prompt: str, letter_type: str) -> Dict[str, Any]:
        """Call Anthropic Claude to generate the letter."""
        response = self.anthropic_client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=2000,
            temperature=0.7,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            system="You are a legal document assistant specializing in debt collection and small claims preparation.",
        )

        content = response.content[0].text if response.content else ""
        usage = response.usage

        # Calculate cost (Claude 3 Opus: $0.015/1K input, $0.075/1K output as of 2024)
        input_cost = (usage.input_tokens / 1000) * 0.015
        output_cost = (usage.output_tokens / 1000) * 0.075
        total_cost = input_cost + output_cost

        return {
            "content": content,
            "provider": "anthropic/claude-3-opus",
            "tokens_used": usage.input_tokens + usage.output_tokens,
            "cost_usd": round(total_cost, 4),
            "model": "claude-3-opus-20240229",
        }


def draft_dispute_letter(
    invoice: Invoice,
    evidence_list: List[Dict[str, Any]],
    letter_type: str = "formal_dispute",
    recipient: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Convenience function to generate a dispute letter.

    Args:
        invoice: Invoice model instance
        evidence_list: List of evidence dictionaries
        letter_type: Type of letter ("formal_dispute", "small_claims_prep", "demand_letter")
        recipient: Optional recipient override

    Returns:
        Dict with content, provider, tokens_used, cost_usd, generated_at

    Raises:
        ValueError: If no AI provider is configured
    """
    generator = DisputeLetterGenerator()
    return generator.draft_dispute_letter(
        invoice, evidence_list, letter_type, recipient
    )
