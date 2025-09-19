# Resume Functionality for PhotoMigrator Google Takeout Processing

## Overview

PhotoMigrator now supports resume functionality that allows you to continue processing from where it stopped if the execution fails or is interrupted. This is particularly useful for large Google Takeout archives that may take hours to process.

## How It Works

### State Tracking
- The tool automatically saves processing state in a file called `processing_state.json` in the output folder
- State is saved after each major step completion
- The state includes:
  - Which steps have been completed
  - Current step and substep
  - Processing start time and last update
  - Error information if processing failed
  - Step duration statistics

### Resume Detection
The tool can automatically detect if a previous run was incomplete by checking:
1. If the output folder exists and contains files
2. If there's a valid `processing_state.json` file
3. If the previous processing was not marked as completed

### Processing Steps
The tool tracks these major processing steps:
1. **Pre-checks** - Validation and unzipping
2. **Pre-processing** - Cleanup and fix truncations
3. **Analyze input files** - Initial file analysis
4. **GPTH processing** - Metadata fixing (main processing step)
5. **Analyze output files** - Final file analysis
6. **Post-processing** - MP4 sync, albums moving, duplicates removal
7. **Final steps** - Statistics and cleanup

## Usage

### Command Line Options

#### Normal Processing
```bash
python PhotoMigrator.py --google-takeout /path/to/takeout
```
This creates a state file automatically for potential resume.

#### Resume Processing
```bash
python PhotoMigrator.py --google-takeout /path/to/takeout --google-resume
```
Use the `--google-resume` flag to resume from a previous incomplete run.

#### Resume with Explicit Output Folder
```bash
python PhotoMigrator.py --google-takeout /path/to/takeout \
                        --output-folder /path/to/previous/output \
                        --google-resume
```

### Resume Behavior

1. **Automatic Detection**: When `--google-resume` is specified, the tool will:
   - Check if the output folder from a previous run exists
   - Validate the state file
   - Display a resume summary showing completed steps and progress
   - Continue from the next incomplete step

2. **Step Skipping**: Completed steps are automatically skipped, showing messages like:
   ```
   ⏭️  STEP 1: Pre-checks already completed, skipping...
   ⏭️  STEP 2: Pre-processing already completed, skipping...
   ```

3. **Progress Restoration**: The tool restores:
   - Step and substep counters
   - Processing statistics and durations
   - Folder paths and configuration

### Resume Summary

When resuming, the tool displays information like:
```
🔄 RESUMING PREVIOUS PROCESSING SESSION...
📋 Resume Summary:
   Input Folder    : /path/to/original/takeout
   Output Folder   : /path/to/output/folder
   Started At      : 2024-01-15T10:30:00
   Last Update     : 2024-01-15T12:45:30
   Progress        : 3/7 steps completed

✅ Completed Steps:
     Step 1: pre_checks
     Step 2: pre_process
     Step 3: analyze_input

⏭️  Next Step      : Step 4: process_gpth
```

## Error Handling

### When Errors Occur
- The tool automatically saves error information to the state file
- Error details are preserved for debugging
- The state file remains intact for resume attempts

### Resume After Error
- Use `--google-resume` to continue from where processing stopped
- The tool will attempt to continue from the next step
- Previous progress is preserved

## State File Details

The `processing_state.json` file contains:
```json
{
  "start_time": "2024-01-15T10:30:00",
  "last_update": "2024-01-15T12:45:30",
  "completed_steps": [1, 2, 3],
  "current_step": 3,
  "current_substep": 0,
  "total_steps": 7,
  "processing_complete": false,
  "error_occurred": false,
  "error_message": "",
  "input_folder": "/path/to/takeout",
  "output_folder": "/path/to/output",
  "steps_duration": [
    {"step_id": 1, "step_name": "Pre-checks", "duration": "0:00:05"},
    {"step_id": 2, "step_name": "Pre-processing", "duration": "0:00:15"}
  ]
}
```

## Limitations

1. **Step Granularity**: Resume works at the step level, not sub-operation level
2. **Configuration Changes**: Changing processing flags between runs may cause issues
3. **File System Changes**: Moving or modifying files between runs may cause problems
4. **Output Folder**: The output folder path must be the same or explicitly specified

## Best Practices

1. **Use Same Configuration**: Keep the same command-line flags when resuming
2. **Don't Modify Files**: Avoid changing files in the output folder between runs
3. **Check Disk Space**: Ensure sufficient space before resuming large operations
4. **Backup State File**: The state file is crucial for resume - don't delete it manually

## Troubleshooting

### Resume Not Working
- Check if the output folder exists and contains files
- Verify the `processing_state.json` file exists and is valid
- Ensure you're using the same takeout folder path
- Use explicit `--output-folder` if the output path has changed

### Invalid State File
- If the state file is corrupted, delete it and start fresh
- The tool will detect missing state files and start normal processing

### State Cleanup
- State files are automatically cleaned up when processing completes successfully
- For failed runs, the state file remains for resume attempts
- You can manually delete `processing_state.json` to force a fresh start

## Examples

### Example 1: Normal Run That Fails
```bash
$ python PhotoMigrator.py --google-takeout MyTakeout/
# ... processing starts ...
# ... fails at step 4 due to disk space issue ...
```

### Example 2: Resume After Fixing Issue
```bash
$ python PhotoMigrator.py --google-takeout MyTakeout/ --google-resume
🔄 RESUMING PREVIOUS PROCESSING SESSION...
📋 Resume Summary:
   Progress: 3/7 steps completed
⏭️  STEP 1: Pre-checks already completed, skipping...
⏭️  STEP 2: Pre-processing already completed, skipping...
⏭️  STEP 3: Input file analysis already completed, skipping...
🧠 [PROCESS] - Continuing with GPTH processing...
```

This resume functionality makes PhotoMigrator much more robust for processing large Google Takeout archives, saving significant time when issues occur during long-running operations.