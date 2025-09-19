# ResumeManager.py
# -*- coding: utf-8 -*-
"""
Resume Manager for PhotoMigrator Google Takeout Processing

This module provides functionality to:
- Detect if a previous run was incomplete
- Save and restore processing state
- Determine which steps need to be resumed or skipped
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path

from Core.CustomLogger import set_log_level
from Core.GlobalVariables import LOGGER, FOLDERNAME_LOGS


class ResumeManager:
    """Manages resume functionality for Google Takeout processing."""
    
    STATE_FILENAME = "processing_state.json"
    
    # Processing steps and their identifiers
    STEPS = {
        1: "pre_checks",
        2: "pre_process", 
        3: "analyze_input",
        4: "process_gpth",
        5: "analyze_output",
        6: "post_process",
        7: "final_steps"
    }
    
    def __init__(self, output_folder, log_level=None):
        """
        Initialize ResumeManager with output folder path.
        
        Args:
            output_folder (str): Path to the output folder where state will be saved
            log_level: Logging level for this operation
        """
        with set_log_level(LOGGER, log_level):
            self.output_folder = Path(output_folder)
            self.state_file = self.output_folder / self.STATE_FILENAME
            self.log_level = log_level
            
            # Initialize default state
            self.state = {
                "start_time": None,
                "last_update": None,
                "completed_steps": [],
                "current_step": 0,
                "current_substep": 0,
                "total_steps": len(self.STEPS),
                "processing_complete": False,
                "error_occurred": False,
                "error_message": "",
                "input_folder": "",
                "output_folder": str(self.output_folder),
                "steps_duration": []
            }
    
    def can_resume(self):
        """
        Check if processing can be resumed.
        
        Returns:
            bool: True if resume is possible, False otherwise
        """
        with set_log_level(LOGGER, self.log_level):
            # Check if output folder exists and has content
            if not self.output_folder.exists():
                LOGGER.debug(f"Resume not possible: output folder does not exist: {self.output_folder}")
                return False
                
            # Check if output folder has any files (not just the state file)
            folder_contents = list(self.output_folder.iterdir())
            if not folder_contents or (len(folder_contents) == 1 and folder_contents[0].name == self.STATE_FILENAME):
                LOGGER.debug(f"Resume not possible: output folder is empty or contains only state file: {self.output_folder}")
                return False
            
            # Check if state file exists and is valid
            if not self.state_file.exists():
                LOGGER.debug(f"Resume not possible: no state file found: {self.state_file}")
                return False
                
            try:
                self.load_state()
                if self.state.get("processing_complete", False):
                    LOGGER.debug("Resume not possible: previous processing was completed successfully")
                    return False
                    
                LOGGER.info(f"Resume possible: found incomplete processing in {self.output_folder}")
                return True
                
            except Exception as e:
                LOGGER.warning(f"Resume not possible: could not load state file: {e}")
                return False
    
    def load_state(self):
        """Load processing state from file."""
        with set_log_level(LOGGER, self.log_level):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    loaded_state = json.load(f)
                    self.state.update(loaded_state)
                LOGGER.debug(f"State loaded from {self.state_file}")
            except (FileNotFoundError, json.JSONDecodeError, PermissionError) as e:
                LOGGER.warning(f"Could not load state file {self.state_file}: {e}")
                raise
    
    def save_state(self):
        """Save current processing state to file."""
        with set_log_level(LOGGER, self.log_level):
            self.state["last_update"] = datetime.now().isoformat()
            
            # Ensure output folder exists
            self.output_folder.mkdir(parents=True, exist_ok=True)
            
            try:
                with open(self.state_file, 'w', encoding='utf-8') as f:
                    json.dump(self.state, f, indent=2, ensure_ascii=False)
                LOGGER.debug(f"State saved to {self.state_file}")
            except (PermissionError, OSError) as e:
                LOGGER.error(f"Could not save state file {self.state_file}: {e}")
    
    def start_processing(self, input_folder):
        """Initialize state for new processing run."""
        with set_log_level(LOGGER, self.log_level):
            self.state.update({
                "start_time": datetime.now().isoformat(),
                "input_folder": str(input_folder),
                "completed_steps": [],
                "current_step": 0,
                "current_substep": 0,
                "processing_complete": False,
                "error_occurred": False,
                "error_message": "",
                "steps_duration": []
            })
            self.save_state()
            LOGGER.info(f"Started new processing session for input: {input_folder}")
    
    def step_completed(self, step_number, step_name="", duration=""):
        """Mark a step as completed."""
        with set_log_level(LOGGER, self.log_level):
            if step_number not in self.state["completed_steps"]:
                self.state["completed_steps"].append(step_number)
                
            self.state["current_step"] = step_number
            
            # Add to steps duration if provided
            if step_name and duration:
                self.state["steps_duration"].append({
                    "step_id": step_number,
                    "step_name": step_name,
                    "duration": duration
                })
            
            self.save_state()
            LOGGER.debug(f"Step {step_number} marked as completed: {step_name}")
    
    def substep_completed(self, step_number, substep_number, step_name="", duration=""):
        """Mark a substep as completed."""
        with set_log_level(LOGGER, self.log_level):
            self.state["current_step"] = step_number
            self.state["current_substep"] = substep_number
            
            # Add to steps duration if provided
            if step_name and duration:
                self.state["steps_duration"].append({
                    "step_id": f"{step_number}.{substep_number}",
                    "step_name": step_name,
                    "duration": duration
                })
            
            self.save_state()
            LOGGER.debug(f"Substep {step_number}.{substep_number} completed: {step_name}")
    
    def is_step_completed(self, step_number):
        """Check if a step has been completed."""
        return step_number in self.state.get("completed_steps", [])
    
    def get_next_step(self):
        """Get the next step that needs to be processed."""
        with set_log_level(LOGGER, self.log_level):
            completed = set(self.state.get("completed_steps", []))
            
            for step_num in sorted(self.STEPS.keys()):
                if step_num not in completed:
                    return step_num
                    
            return None  # All steps completed
    
    def mark_completed(self):
        """Mark processing as successfully completed."""
        with set_log_level(LOGGER, self.log_level):
            self.state.update({
                "processing_complete": True,
                "current_step": len(self.STEPS),
                "last_update": datetime.now().isoformat()
            })
            self.save_state()
            LOGGER.info("Processing marked as completed successfully")
    
    def mark_error(self, error_message):
        """Mark processing as failed due to error."""
        with set_log_level(LOGGER, self.log_level):
            self.state.update({
                "error_occurred": True,
                "error_message": str(error_message),
                "last_update": datetime.now().isoformat()
            })
            self.save_state()
            LOGGER.error(f"Processing marked as failed: {error_message}")
    
    def get_resume_summary(self):
        """Get a summary of what will be resumed."""
        with set_log_level(LOGGER, self.log_level):
            if not self.can_resume():
                return None
                
            completed_steps = self.state.get("completed_steps", [])
            next_step = self.get_next_step()
            
            summary = {
                "input_folder": self.state.get("input_folder", ""),
                "output_folder": self.state.get("output_folder", ""),
                "start_time": self.state.get("start_time", ""),
                "last_update": self.state.get("last_update", ""),
                "completed_steps": [f"Step {s}: {self.STEPS.get(s, 'Unknown')}" for s in sorted(completed_steps)],
                "next_step": f"Step {next_step}: {self.STEPS.get(next_step, 'Unknown')}" if next_step else "All steps completed",
                "progress": f"{len(completed_steps)}/{len(self.STEPS)} steps completed"
            }
            
            return summary
    
    def cleanup_state_file(self):
        """Remove the state file (used when processing completes successfully)."""
        with set_log_level(LOGGER, self.log_level):
            try:
                if self.state_file.exists():
                    self.state_file.unlink()
                    LOGGER.debug(f"Cleaned up state file: {self.state_file}")
            except OSError as e:
                LOGGER.warning(f"Could not remove state file {self.state_file}: {e}")