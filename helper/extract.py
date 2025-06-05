"""Helper functions for extracting SOAP components from transcribed text using OpenAI GPT."""

import asyncio
import json
from typing import List
import openai
from tenacity import retry, stop_after_attempt, wait_exponential
from pydantic import ValidationError
from datetime import date

from config import settings
from models.soap import SoapModel
from app_logging import get_logger

logger = get_logger(__name__)

# Initialize OpenAI client
openai_client = openai.AsyncOpenAI(api_key=settings.openai_api_key)

# Comprehensive SOAP extraction prompt
SOAP_EXTRACTION_PROMPT = """You are an expert physiotherapist and clinical documentation specialist. Your task is to extract structured SOAP (Subjective, Objective, Assessment, Plan) information from a transcribed therapy session.

## SOAP Documentation Guidelines:

### SUBJECTIVE (Patient's Self-Report):
- Patient's description of symptoms, pain levels (use 0-10 scale when mentioned)
- Functional limitations and how they impact daily activities
- Changes since last treatment or onset of condition
- Patient's goals and concerns
- Sleep, work, and activity modifications
- Medication use and effects
- Previous treatments tried

Common Pitfalls to Avoid:
- Don't include therapist observations in subjective section
- Don't interpret patient statements - record them as reported
- Don't include objective measurements here

### OBJECTIVE (Clinical Findings):
- Range of motion measurements (degrees, percentages)
- Strength testing results (MMT grades, dynamometer readings)
- Functional assessments and standardized test scores
- Gait analysis and movement patterns
- Palpation findings
- Special tests and their results
- Postural assessment
- Vital signs if relevant

Common Pitfalls to Avoid:
- Don't include subjective patient reports
- Be specific with measurements and grades
- Don't make assumptions about findings not explicitly stated

### ASSESSMENT (Clinical Judgment):
- Clinical reasoning combining subjective and objective findings
- Progress toward established goals
- Changes in functional status
- Prognosis and rehabilitation potential
- Response to previous interventions
- Problem identification and prioritization

Common Pitfalls to Avoid:
- Don't just restate findings - analyze and interpret them
- Connect subjective reports with objective findings
- Address functional implications

### PLAN (Treatment Strategy):
- Interventions performed in this session
- Home exercise program and modifications
- Education provided to patient
- Goals for upcoming sessions
- Frequency and duration of future treatments
- Referrals or consultations needed
- Equipment or assistive device recommendations

Common Pitfalls to Avoid:
- Be specific about exercise parameters (sets, reps, frequency)
- Include both short-term and long-term planning
- Don't forget patient education components

## Additional Clinical Context:
- Always consider the whole person, not just the injury
- Document functional improvements or limitations
- Include safety considerations and precautions
- Note patient compliance and understanding
- Consider psychosocial factors affecting recovery

## Output Requirements:
You must return ONLY a valid JSON object that matches the SoapModel schema. Do not include any explanations, markdown formatting, or additional text.

The JSON must include these required fields:
- patient_name (extract from conversation or use "Not specified" if unclear)
- session_date (today's date if not mentioned: {today_date})
- subjective (minimum 10 characters)
- objective (minimum 10 characters) 
- assessment (minimum 10 characters)
- plan (minimum 10 characters)

Optional fields you may include if information is available:
- patient_id
- therapist_name
- session_duration
- chief_complaint
- treatment_goals
- follow_up_date

Now extract SOAP information from this transcribed session:"""


async def chunk_text_if_needed(text: str, max_tokens: int = None) -> List[str]:
    """
    Split text into chunks if it exceeds token limits.
    
    Args:
        text: The input text to potentially chunk
        max_tokens: Maximum tokens per chunk (defaults to settings.max_tokens - buffer)
        
    Returns:
        List of text chunks
    """
    if max_tokens is None:
        max_tokens = settings.max_tokens - 500  # Buffer for prompt and response
    
    # Rough estimation: 1 token ≈ 4 characters
    estimated_tokens = len(text) // 4
    
    if estimated_tokens <= max_tokens:
        return [text]
    
    logger.warning("Text exceeds token limit, chunking required",
                  estimated_tokens=estimated_tokens,
                  max_tokens=max_tokens)
    
    # Split by sentences, then recombine to fit token limits
    sentences = text.split('. ')
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        # Check if adding this sentence would exceed the limit
        if len(current_chunk + sentence) // 4 > max_tokens:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence + '. '
            else:
                # Single sentence is too long, truncate it
                chunks.append(sentence[:max_tokens * 4])
        else:
            current_chunk += sentence + '. '
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def extract_soap_from_text(text: str) -> SoapModel:
    """
    Extract SOAP information from transcribed text using OpenAI GPT.
    
    Args:
        text: Transcribed therapy session text
        
    Returns:
        Validated SoapModel instance
        
    Raises:
        Exception: If extraction fails after retries
    """
    logger.info("Starting SOAP extraction", text_length=len(text))
    
    # Add today's date to the prompt
    today_date = date.today().isoformat()
    full_prompt = SOAP_EXTRACTION_PROMPT.format(today_date=today_date)
    
    try:
        # Check if text needs chunking
        chunks = await chunk_text_if_needed(text)
        
        if len(chunks) > 1:
            logger.info("Processing multiple text chunks", chunk_count=len(chunks))
            # For multiple chunks, we'll process them separately and combine
            # This is a simplified approach - in production, you might want more sophisticated merging
            combined_text = " ".join(chunks[:2])  # Use first 2 chunks for now
        else:
            combined_text = chunks[0]
        
        response = await openai_client.chat.completions.create(
            model=settings.openai_model_gpt,
            messages=[
                {
                    "role": "system",
                    "content": full_prompt
                },
                {
                    "role": "user", 
                    "content": combined_text
                }
            ],
            max_tokens=settings.max_tokens,
            temperature=0.1,  # Low temperature for consistent extraction
            response_format={"type": "json_object"}
        )
        
        # Parse the JSON response
        soap_data = json.loads(response.choices[0].message.content)
        
        # Validate using Pydantic model
        soap_model = SoapModel.model_validate(soap_data)
        
        logger.info("SOAP extraction completed successfully",
                   text_length=len(text),
                   patient_name=soap_model.patient_name)
        
        return soap_model
        
    except json.JSONDecodeError as e:
        logger.error("Failed to parse JSON response", error=str(e))
        raise ValueError(f"Invalid JSON response from GPT: {str(e)}")
        
    except ValidationError as e:
        logger.error("SOAP validation failed", error=str(e))
        # Try to re-prompt with validation guidance
        raise ValueError(f"SOAP validation failed: {str(e)}")
        
    except Exception as e:
        logger.error("SOAP extraction failed", error=str(e))
        raise


async def extract_soap(text: str) -> SoapModel:
    """
    Extract SOAP with automatic retry and validation guidance.
    
    Args:
        text: Transcribed therapy session text
        
    Returns:
        Validated SoapModel instance
    """
    if not text or len(text.strip()) < 50:
        raise ValueError("Text is too short for meaningful SOAP extraction")
    
    try:
        return await extract_soap_from_text(text)
    except ValidationError as e:
        logger.warning("First extraction failed validation, retrying with guidance")
        
        # Create a guidance prompt based on the validation error
        guidance_prompt = f"""
        The previous extraction failed validation with these errors:
        {str(e)}
        
        Please ensure:
        1. All required fields (patient_name, session_date, subjective, objective, assessment, plan) are included
        2. Each text field has at least 10 characters
        3. Dates are in YYYY-MM-DD format
        4. session_duration (if included) is between 15 and 180 minutes
        
        Re-extract the SOAP information with these corrections:
        """
        
        try:
            response = await openai_client.chat.completions.create(
                model=settings.openai_model_gpt,
                messages=[
                    {
                        "role": "system",
                        "content": SOAP_EXTRACTION_PROMPT + guidance_prompt
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                max_tokens=settings.max_tokens,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            soap_data = json.loads(response.choices[0].message.content)
            return SoapModel.model_validate(soap_data)
            
        except Exception as retry_error:
            logger.error("Retry extraction also failed", error=str(retry_error))
            raise ValueError(f"SOAP extraction failed after retry: {str(retry_error)}")
