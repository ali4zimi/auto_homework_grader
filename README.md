# Automated JUnit Testing System

A Python-based application for automated testing and grading of student Java submissions.

## Project Structure

```
auto_junit/
├── app.py                      # Main application
├── config/
│   └── settings.py            # Configuration settings
├── lib/
│   └── junit-platform-console-standalone-1.14.1.jar
├── tests/
│   └── TestInTheSky.java      # JUnit test file
├── output/
│   └── grades.csv             # Generated grades
├── temp_dir/                  # Temporary working directory
├── Homeworks/
│   ├── done/                  # Processed submissions
│   └── [student folders]      # Pending submissions
└── README.md                  # This file
```

## Requirements

- Python 3.7+
- Java JDK 21+ (configured in config/settings.py)
- JUnit Platform Console Standalone JAR (1.14.1)

## Configuration

Edit `config/settings.py` to customize:
- JDK path
- Directory locations
- Test file names
- Java compilation settings

## Usage

1. Place student submissions in `Homeworks/` directory
2. Ensure JUnit JAR is in `lib/` folder
3. Place test file in `tests/` folder
4. Run the application:

```bash
python app.py
```

5. Follow the interactive prompts to:
   - Review submission list
   - View test results
   - Enter grades (Task 1, Task 2, Task 3)
   - Add comments

## Workflow

1. **Scan**: Scans `Homeworks/` directory (excludes `done/` folder)
2. **Display**: Shows table with student names, matriculation numbers, and submission types
3. **Process**: For each student:
   - Extracts zip files (if applicable)
   - Copies Java files to temp directory
   - Compiles with JUnit in classpath
   - Runs automated tests
   - Prompts for grades
   - Saves to CSV
   - Moves folder to `done/`
4. **Complete**: All grades saved to `output/grades.csv`

## Submission Types

- 🟡 **Zipped file** (.zip, .rar, .7z)
- 🟢 **Text file** (.txt)
- 🔵 **Folder**
- 🔴 **Unknown/Other**

## Output

Grades are saved in CSV format with columns:
- Student Name
- Matriculation Nr
- Task 1
- Task 2
- Task 3
- Comment

## Resuming Sessions

The system supports pausing and resuming:
- Processed submissions are moved to `Homeworks/done/`
- CSV file accumulates grades across sessions
- Rerun `app.py` to continue with remaining submissions

## Error Handling

- Validates Java installation
- Checks for required files (tests, JUnit JAR)
- Reports compilation errors
- Handles missing matriculation numbers
- Skips `_MACOSX` directories in zip files

## Author

Created for automated grading of Java homework assignments.
