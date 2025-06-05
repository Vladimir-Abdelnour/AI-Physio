"""Helper functions for rendering SOAP models into Markdown reports."""

import asyncio
from pathlib import Path
from datetime import datetime

from config import settings
from models.soap import SoapModel
from app_logging import get_logger

logger = get_logger(__name__)


def render_soap_to_markdown(soap_model: SoapModel, output_path: str) -> str:
    """
    Render SOAP model to Markdown format.
    
    Args:
        soap_model: The SoapModel instance to render
        output_path: Path for the output Markdown file
        
    Returns:
        Path to the generated Markdown file
    """
    markdown_content = f"""# SOAP Report
## Physiotherapy Session Documentation

---

### Patient Information
- **Patient Name:** {soap_model.patient_name}
- **Session Date:** {soap_model.session_date}
"""

    if soap_model.therapist_name:
        markdown_content += f"- **Therapist:** {soap_model.therapist_name}\n"
    
    if soap_model.session_duration:
        markdown_content += f"- **Session Duration:** {soap_model.session_duration} minutes\n"
    
    if soap_model.chief_complaint:
        markdown_content += f"- **Chief Complaint:** {soap_model.chief_complaint}\n"

    markdown_content += f"""
---

## SUBJECTIVE

{soap_model.subjective}

---

## OBJECTIVE

{soap_model.objective}

---

## ASSESSMENT

{soap_model.assessment}

---

## PLAN

{soap_model.plan}

---
"""

    if soap_model.treatment_goals:
        markdown_content += f"""
### Treatment Goals

{soap_model.treatment_goals}

---
"""

    if soap_model.follow_up_date:
        markdown_content += f"""
### Follow-up Information

- **Next Appointment:** {soap_model.follow_up_date}

---
"""

    markdown_content += f"""
*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    return output_path


async def render_soap_to_pdf(soap_model: SoapModel, output_filename: str = None) -> str:
    """
    Render a SOAP model to Markdown format (changed from PDF to avoid dependency issues).
    
    Args:
        soap_model: The SoapModel instance to render
        output_filename: Optional custom filename for the output
        
    Returns:
        Path to the generated Markdown file
        
    Raises:
        Exception: If rendering fails
    """
    logger.info("Starting Markdown rendering", patient_name=soap_model.patient_name)
    
    try:
        # Generate filename if not provided
        if not output_filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_patient_name = "".join(c for c in soap_model.patient_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_patient_name = safe_patient_name.replace(' ', '_')
            output_filename = f"SOAP_{safe_patient_name}_{timestamp}.md"
        
        if not output_filename.endswith('.md'):
            output_filename += '.md'
        
        # Ensure output directory exists
        settings.pdf_output_dir.mkdir(parents=True, exist_ok=True)
        output_path = settings.pdf_output_dir / output_filename
        
        # Generate Markdown
        logger.info("Generating Markdown report", output_path=str(output_path))
        render_soap_to_markdown(soap_model, str(output_path))
        
        logger.info("Markdown report generated successfully", 
                   output_path=str(output_path),
                   patient_name=soap_model.patient_name)
        
        return str(output_path)
        
    except Exception as e:
        logger.error("Markdown rendering failed", error=str(e))
        raise RuntimeError(f"Markdown rendering failed: {str(e)}")
