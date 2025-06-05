"""SOAP model definitions for physiotherapy session documentation."""

from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, validator


class SoapModel(BaseModel):
    """
    Structured SOAP (Subjective, Objective, Assessment, Plan) model for physiotherapy sessions.
    
    This model represents a complete physiotherapy session documentation following
    the SOAP format widely used in healthcare documentation.
    """
    
    # Core SOAP fields
    patient_name: str = Field(
        ..., 
        examples=["Jane Doe"],
        description="Full name of the patient receiving treatment"
    )
    
    session_date: date = Field(
        ...,
        description="Date when the therapy session took place"
    )
    
    subjective: str = Field(
        ...,
        description="""Patient's self-reported symptoms, pain levels, functional limitations, 
        and any changes since the last session. Includes patient's perspective on their condition.""",
        min_length=10
    )
    
    objective: str = Field(
        ...,
        description="""Measurable and observable findings including range of motion, strength testing,
        functional assessments, gait analysis, and any diagnostic tests performed.""",
        min_length=10
    )
    
    assessment: str = Field(
        ...,
        description="""Professional clinical judgment combining subjective and objective findings.
        Includes progress toward goals, clinical reasoning, and any changes to diagnosis.""",
        min_length=10
    )
    
    plan: str = Field(
        ...,
        description="""Treatment plan including interventions performed, exercises prescribed,
        education provided, and plans for future sessions including frequency and duration.""",
        min_length=10
    )
    
    # Optional metadata fields
    patient_id: Optional[str] = Field(
        None,
        description="Unique identifier for the patient in the clinic's system"
    )
    
    therapist_name: Optional[str] = Field(
        None,
        description="Name of the treating physiotherapist"
    )
    
    clinic_logo_url: Optional[str] = Field(
        None,
        description="URL or path to clinic logo for report header"
    )
    
    therapist_signature_url: Optional[str] = Field(
        None,
        description="URL or path to therapist's signature for report footer"
    )
    
    follow_up_date: Optional[date] = Field(
        None,
        description="Scheduled date for next appointment or follow-up"
    )
    
    # Additional clinical fields
    session_duration: Optional[int] = Field(
        None,
        description="Duration of the therapy session in minutes",
        ge=15,  # Minimum 15 minutes
        le=180  # Maximum 3 hours
    )
    
    chief_complaint: Optional[str] = Field(
        None,
        description="Primary reason for the patient's visit"
    )
    
    treatment_goals: Optional[str] = Field(
        None,
        description="Short and long-term treatment goals"
    )
    
    @validator('session_date')
    def validate_session_date(cls, v):
        """Ensure session date is not in the future."""
        if v > date.today():
            raise ValueError('Session date cannot be in the future')
        return v
    
    @validator('follow_up_date')
    def validate_follow_up_date(cls, v, values):
        """Ensure follow-up date is after session date."""
        if v is not None and 'session_date' in values:
            if v <= values['session_date']:
                raise ValueError('Follow-up date must be after session date')
        return v
    
    class Config:
        """Pydantic configuration."""
        
        # Enable JSON schema generation
        json_schema_extra = {
            "example": {
                "patient_name": "John Smith",
                "session_date": "2024-01-15",
                "subjective": "Patient reports decreased lower back pain (3/10) compared to last week (7/10). Able to sit for longer periods without discomfort. Still experiencing stiffness in the morning lasting approximately 30 minutes.",
                "objective": "ROM: Lumbar flexion 75% of normal, extension 80% of normal. SLR test negative bilaterally. Core strength testing shows improvement in plank hold time from 30s to 45s. Gait pattern normalized with minimal antalgic component.",
                "assessment": "Patient showing significant improvement in lumbar spine mobility and pain levels. Functional capacity improving with core strengthening program. Ready to progress to next phase of rehabilitation focusing on dynamic stability.",
                "plan": "Continue current exercise program with progression: increase plank hold to 60s, add side planks, introduce dynamic movement patterns. Home exercise program reviewed. Next session in 3 days to monitor progress and advance treatment as appropriate.",
                "patient_id": "PT001234",
                "therapist_name": "Dr. Sarah Johnson, PT, DPT",
                "session_duration": 60,
                "chief_complaint": "Lower back pain following lifting injury",
                "treatment_goals": "Reduce pain to 0-1/10, restore full ROM, return to work activities without limitations",
                "follow_up_date": "2024-01-18"
            }
        }
        
        # Allow field aliases for API compatibility
        populate_by_name = True
        
        # Validate assignments
        validate_assignment = True 