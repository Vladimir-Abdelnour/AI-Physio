"""
PhysioSOAP MVP Workflow - Simplified AI Agent Orchestrator

This module contains the main AI agent that orchestrates the complete pipeline:
Audio → Transcription → SOAP Extraction → Markdown Generation

The agent uses direct helper functions for each component and handles the full workflow
with proper error handling, logging, and resilience.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import argparse
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.table import Table

from helper import transcribe, extract, render
from models.soap import SoapModel
from config import settings
from app_logging import get_logger

logger = get_logger(__name__)
console = Console()


class PhysioSOAPAgent:
    """
    Main AI agent that orchestrates the complete PhysioSOAP workflow.
    
    This agent manages the full pipeline from audio input to PDF output,
    coordinating between transcription, extraction, and rendering functions.
    """
    
    def __init__(self):
        self.workflow_stats: Dict[str, Any] = {}
    
    async def process_audio_to_soap(
        self, 
        audio_path: str, 
        output_filename: str = None
    ) -> Dict[str, Any]:
        """
        Complete workflow: Process audio file to generate SOAP Markdown report.
        
        Args:
            audio_path: Path to the audio file to process
            output_filename: Optional custom filename for the Markdown output
            
        Returns:
            Dictionary containing workflow results and metadata
            
        Raises:
            ValueError: If audio file is invalid
            RuntimeError: If any step in the workflow fails
        """
        start_time = datetime.now()
        workflow_id = f"workflow_{start_time.strftime('%Y%m%d_%H%M%S')}"
        
        logger.info("Starting PhysioSOAP workflow", 
                   workflow_id=workflow_id,
                   audio_path=audio_path)
        
        # Initialize workflow stats
        self.workflow_stats = {
            "workflow_id": workflow_id,
            "start_time": start_time,
            "audio_path": audio_path,
            "steps_completed": [],
            "errors": []
        }
        
        try:
            # Validate audio file
            audio_file = Path(audio_path)
            if not audio_file.exists():
                raise ValueError(f"Audio file not found: {audio_path}")
            
            # Step 1: Transcription
            console.print("\n[bold cyan]Step 1: Audio Transcription[/bold cyan]")
            console.print(f"Processing: {audio_file.name}")
            
            transcription_start = datetime.now()
            transcribed_text = await transcribe.transcribe_audio(audio_path)
            transcription_time = (datetime.now() - transcription_start).total_seconds()
            
            self.workflow_stats["transcription"] = {
                "duration_seconds": transcription_time,
                "text_length": len(transcribed_text),
                "completed_at": datetime.now()
            }
            self.workflow_stats["steps_completed"].append("transcription")
            
            console.print(f"[green]✓ Transcription completed ({transcription_time:.1f}s)[/green]")
            console.print(f"Transcribed text length: {len(transcribed_text)} characters")
            
            # Step 2: SOAP Extraction
            console.print("\n[bold cyan]Step 2: SOAP Information Extraction[/bold cyan]")
            
            extraction_start = datetime.now()
            soap_model = await extract.extract_soap(transcribed_text)
            extraction_time = (datetime.now() - extraction_start).total_seconds()
            
            self.workflow_stats["extraction"] = {
                "duration_seconds": extraction_time,
                "patient_name": soap_model.patient_name,
                "session_date": str(soap_model.session_date),
                "completed_at": datetime.now()
            }
            self.workflow_stats["steps_completed"].append("extraction")
            
            console.print(f"[green]✓ SOAP extraction completed ({extraction_time:.1f}s)[/green]")
            console.print(f"Patient: {soap_model.patient_name}")
            console.print(f"Session Date: {soap_model.session_date}")
            
            # Step 3: Markdown Rendering
            console.print("\n[bold cyan]Step 3: Markdown Report Generation[/bold cyan]")
            
            rendering_start = datetime.now()
            markdown_path = await render.render_soap_to_pdf(soap_model, output_filename)
            rendering_time = (datetime.now() - rendering_start).total_seconds()
            
            self.workflow_stats["rendering"] = {
                "duration_seconds": rendering_time,
                "markdown_path": markdown_path,
                "completed_at": datetime.now()
            }
            self.workflow_stats["steps_completed"].append("rendering")
            
            console.print(f"[green]✓ Markdown generation completed ({rendering_time:.1f}s)[/green]")
            console.print(f"Markdown saved: {markdown_path}")
            
            # Workflow completed successfully
            total_time = (datetime.now() - start_time).total_seconds()
            self.workflow_stats["total_duration_seconds"] = total_time
            self.workflow_stats["status"] = "completed"
            self.workflow_stats["end_time"] = datetime.now()
            
            logger.info("PhysioSOAP workflow completed successfully",
                       workflow_id=workflow_id,
                       total_duration=total_time,
                       patient_name=soap_model.patient_name)
            
            # Display summary
            self._display_workflow_summary()
            
            return {
                "status": "success",
                "workflow_stats": self.workflow_stats,
                "soap_model": soap_model,
                "markdown_path": markdown_path,
                "transcribed_text": transcribed_text
            }
            
        except Exception as e:
            error_time = datetime.now()
            error_info = {
                "error": str(e),
                "error_type": type(e).__name__,
                "occurred_at": error_time
            }
            
            self.workflow_stats["errors"].append(error_info)
            self.workflow_stats["status"] = "failed"
            self.workflow_stats["end_time"] = error_time
            
            logger.error("PhysioSOAP workflow failed",
                        workflow_id=workflow_id,
                        error=str(e),
                        steps_completed=self.workflow_stats["steps_completed"])
            
            console.print(f"\n[bold red]✗ Workflow failed: {str(e)}[/bold red]")
            
            raise RuntimeError(f"PhysioSOAP workflow failed: {str(e)}")
    
    def _display_workflow_summary(self) -> None:
        """Display a summary of the completed workflow."""
        
        console.print("\n" + "="*60)
        console.print(Panel.fit(
            "[bold green]PhysioSOAP Workflow Completed Successfully![/bold green]",
            style="green"
        ))
        
        # Create summary table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Step", style="cyan")
        table.add_column("Duration", style="green")
        table.add_column("Status", style="bold green")
        
        for step in ["transcription", "extraction", "rendering"]:
            if step in self.workflow_stats:
                duration = f"{self.workflow_stats[step]['duration_seconds']:.1f}s"
                table.add_row(step.title(), duration, "✓ Completed")
        
        console.print(table)
        
        # Display key information
        console.print(f"\n[bold]Workflow ID:[/bold] {self.workflow_stats['workflow_id']}")
        console.print(f"[bold]Total Duration:[/bold] {self.workflow_stats['total_duration_seconds']:.1f} seconds")
        
        if "extraction" in self.workflow_stats:
            console.print(f"[bold]Patient:[/bold] {self.workflow_stats['extraction']['patient_name']}")
            console.print(f"[bold]Session Date:[/bold] {self.workflow_stats['extraction']['session_date']}")
        
        if "rendering" in self.workflow_stats:
            console.print(f"[bold]Markdown Report:[/bold] {self.workflow_stats['rendering']['markdown_path']}")
        
        console.print("="*60)


async def main():
    """Main entry point for the PhysioSOAP AI agent."""
    
    parser = argparse.ArgumentParser(
        description="PhysioSOAP MVP - Convert therapy session audio to SOAP Markdown reports"
    )
    parser.add_argument(
        "audio_path",
        help="Path to the audio file to process"
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Custom filename for the Markdown output (without extension)",
        default=None
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    try:
        console.print(Panel.fit(
            "[bold blue]PhysioSOAP MVP - AI Agent[/bold blue]\n"
            "Converting therapy session audio to structured SOAP reports",
            style="blue"
        ))
        
        agent = PhysioSOAPAgent()
        result = await agent.process_audio_to_soap(
            audio_path=args.audio_path,
            output_filename=args.output
        )
        
        console.print(f"\n[bold green]Success![/bold green] Markdown report generated: {result['markdown_path']}")
        return 0
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Workflow interrupted by user[/yellow]")
        return 1
        
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
        logger.error("Main workflow failed", error=str(e))
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 