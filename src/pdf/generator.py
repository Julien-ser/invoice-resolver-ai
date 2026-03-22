"""
PDF generation for dispute letters and small claims forms.

This module provides utilities to convert HTML templates to PDF using WeasyPrint,
with pre-built templates for dispute letters and small claims court forms.
"""

import os
from pathlib import Path
from typing import Optional, Union, Dict, Any
from io import BytesIO

from weasyprint import HTML, CSS
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from jinja2.exceptions import TemplateNotFound, UndefinedError

from src.core.config import settings


class PDFGenerator:
    """Generates PDF documents from HTML content and templates."""

    def __init__(self, templates_dir: Optional[str] = None):
        """
        Initialize PDF generator.

        Args:
            templates_dir: Directory containing HTML templates.
                          Defaults to src/pdf/templates if not provided.
        """
        if templates_dir is None:
            templates_dir = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "templates"
            )
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)), undefined=StrictUndefined
        )

    def generate_pdf(
        self,
        html_content: str,
        output_path: Optional[Union[str, Path]] = None,
        css_styles: Optional[str] = None,
        page_size: str = "A4",
        margins: Optional[Dict[str, str]] = None,
    ) -> Union[bytes, Path]:
        """
        Generate PDF from HTML content.

        Args:
            html_content: HTML string to convert to PDF
            output_path: Optional path to save PDF file. If None, returns bytes
            css_styles: Optional additional CSS styles to apply
            page_size: Page size (default A4)
            margins: Dict with margin values (top, right, bottom, left)
                     Default: {"top": "1cm", "right": "1cm", "bottom": "1cm", "left": "1cm"}

        Returns:
            If output_path provided: Path to saved PDF file
            If output_path None: bytes object containing PDF data
        """
        if margins is None:
            margins = {"top": "1cm", "right": "1cm", "bottom": "1cm", "left": "1cm"}

        # Build CSS
        base_css = f"""
        @page {{
            size: {page_size};
            margin: {margins["top"]} {margins["right"]} {margins["bottom"]} {margins["left"]};
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
        }}
        h1, h2, h3 {{
            color: #2c3e50;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
        }}
        .header {{
            text-align: center;
            border-bottom: 2px solid #2c3e50;
            padding-bottom: 1em;
            margin-bottom: 2em;
        }}
        .footer {{
            text-align: center;
            font-size: 0.9em;
            color: #666;
            border-top: 1px solid #ddd;
            padding-top: 0.5em;
            margin-top: 2em;
        }}
        .invoice-details {{
            background: #f8f9fa;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 1em;
            margin: 1em 0;
        }}
        .evidence-item {{
            margin: 0.5em 0;
            padding: 0.5em;
            background: #fff;
            border-left: 3px solid #3498db;
        }}
        .highlight {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            padding: 0.5em;
            border-radius: 3px;
        }}
        .payment-info {{
            background: #d4edda;
            border: 1px solid #c3e6cb;
            padding: 1em;
            border-radius: 4px;
            margin: 1em 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1em 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 0.75em;
            text-align: left;
        }}
        th {{
            background: #f2f2f2;
            font-weight: bold;
        }}
        """

        if css_styles:
            base_css += css_styles

        # Create WeasyPrint HTML object
        doc = HTML(string=html_content, base_url=str(self.templates_dir))
        doc = doc.render(stylesheets=[CSS(string=base_css)])

        if output_path:
            # Save to file
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            doc.write_pdf(str(output_path))
            return output_path
        else:
            # Return bytes
            pdf_bytes = BytesIO()
            doc.write_pdf(pdf_bytes)
            return pdf_bytes.getvalue()

    def render_template(
        self,
        template_name: str,
        context: Dict[str, Any],
        output_path: Optional[Union[str, Path]] = None,
        **kwargs,
    ) -> Union[bytes, Path]:
        """
        Render an HTML template with context and generate PDF.

        Args:
            template_name: Name of template file (e.g., 'dispute_letter.html')
            context: Dictionary of variables to inject into template
            output_path: Optional path to save PDF
            **kwargs: Additional arguments passed to generate_pdf()

        Returns:
            PDF bytes or Path to saved file

        Raises:
            FileNotFoundError: If the template file does not exist
            ValueError: If template rendering fails for other reasons (including missing variables)
        """
        try:
            template = self.jinja_env.get_template(template_name)
            html_content = template.render(**context)
        except TemplateNotFound:
            raise FileNotFoundError(
                f"Template '{template_name}' not found in {self.templates_dir}"
            )
        except UndefinedError as e:
            raise ValueError(f"Missing template variable: {e}")
        except Exception as e:
            raise ValueError(f"Failed to render template {template_name}: {e}")

        return self.generate_pdf(html_content, output_path, **kwargs)


# Convenience function
def generate_pdf(
    html_content: str,
    output_path: Optional[Union[str, Path]] = None,
    **kwargs,
) -> Union[bytes, Path]:
    """
    Convenience function to generate PDF without instantiating PDFGenerator.

    Args:
        html_content: HTML string to convert
        output_path: Optional output file path
        **kwargs: Additional options passed to PDFGenerator.generate_pdf()

    Returns:
        PDF bytes or Path to saved file
    """
    generator = PDFGenerator()
    return generator.generate_pdf(html_content, output_path, **kwargs)
