"""
================================================================================
    Automated JUnit Testing System for Student Submissions
    
    This application automates the process of:
    - Scanning student homework submissions
    - Extracting and compiling Java files
    - Running JUnit tests
    - Collecting grades and generating CSV reports
    - Organizing processed submissions
================================================================================
"""

import os
import re
import zipfile
import shutil
import subprocess
import csv
import json
import glob


# ============================================================================
#  Configuration & Constants
# ============================================================================

class Colors:
    """ANSI color codes for terminal output formatting"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'


CONFIG_FILE = 'config/settings.json'
Config = {}


# ============================================================================
#  Configuration Management Functions
# ============================================================================

def load_config():
    """
    ╔══════════════════════════════════════════════════════════════════════╗
    ║  Load Configuration                                                  ║
    ╠══════════════════════════════════════════════════════════════════════╣
    ║  Loads configuration from JSON file. If file doesn't exist,          ║
    ║  triggers initialization phase. If file exists, asks user whether    ║
    ║  to use current settings or reconfigure.                             ║
    ║                                                                      ║
    ║  Returns:                                                            ║
    ║      dict: Configuration dictionary                                  ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """
    global Config
    
    # If config file doesn't exist, run first-time setup
    if not os.path.exists(CONFIG_FILE):
        print(f"{Colors.YELLOW}Configuration file not found. Running first-time setup...{Colors.RESET}\n")
        Config = init_setup()
        return Config
    
    # Config file exists - ask user what to do
    print(f"\n{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BLUE}  CONFIGURATION{Colors.RESET}".center(88))
    print(f"{Colors.BLUE}{'='*80}{Colors.RESET}\n")
    
    print("What would you like to do?")
    print(f"  1. {Colors.GREEN}Run with current settings{Colors.RESET}")
    print(f"  2. {Colors.YELLOW}Reconfigure (run setup wizard){Colors.RESET}")
    
    while True:
        choice = input("\nEnter your choice (1 or 2): ").strip()
        if choice == '1':
            # Load existing config
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                Config = json.load(f)
            print(f"{Colors.GREEN}Using existing configuration.{Colors.RESET}\n")
            return Config
        elif choice == '2':
            # Run setup wizard
            print(f"\n{Colors.YELLOW}Starting reconfiguration...{Colors.RESET}\n")
            Config = init_setup()
            return Config
        else:
            print(f"{Colors.RED}Invalid choice. Please enter 1 or 2.{Colors.RESET}")



def save_config(config):
    """
    ╔══════════════════════════════════════════════════════════════════════╗
    ║  Save Configuration                                                  ║
    ╠══════════════════════════════════════════════════════════════════════╣
    ║  Saves configuration dictionary to JSON file.                        ║
    ║                                                                      ║
    ║  Args:                                                               ║
    ║      config (dict): Configuration dictionary to save                 ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """
    # Ensure config directory exists
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)
    
    print(f"{Colors.GREEN}Configuration saved to {CONFIG_FILE}{Colors.RESET}\n")


def find_java_jdk():
    """
    ╔══════════════════════════════════════════════════════════════════════╗
    ║  Find Java JDK                                                       ║
    ╠══════════════════════════════════════════════════════════════════════╣
    ║  Attempts to automatically find Java JDK installations on Windows.   ║
    ║                                                                      ║
    ║  Returns:                                                            ║
    ║      list: List of found JDK bin paths                               ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """
    potential_paths = []
    
    # Check common JDK installation locations
    common_locations = [
        r"C:\Program Files\Java\*",
        r"C:\Program Files (x86)\Java\*",
        r"C:\Program Files\Eclipse Adoptium\*",
        r"C:\Program Files\Microsoft\*"
    ]
    
    for location_pattern in common_locations:
        for jdk_dir in glob.glob(location_pattern):
            bin_path = os.path.join(jdk_dir, 'bin')
            if os.path.exists(bin_path):
                java_exe = os.path.join(bin_path, 'java.exe')
                javac_exe = os.path.join(bin_path, 'javac.exe')
                if os.path.exists(java_exe) and os.path.exists(javac_exe):
                    potential_paths.append(bin_path)
    
    return potential_paths


def init_setup():
    """
    ╔══════════════════════════════════════════════════════════════════════╗
    ║  Initialize Setup                                                    ║
    ╠══════════════════════════════════════════════════════════════════════╣
    ║  First-time setup wizard that:                                       ║
    ║  1. Asks for JDK path (with auto-detection)                          ║
    ║  2. Scans and lists available test files                             ║
    ║  3. Asks user to select test file                                    ║
    ║  4. Creates required directories                                     ║
    ║  5. Saves configuration to JSON                                      ║
    ║                                                                      ║
    ║  Returns:                                                            ║
    ║      dict: Configuration dictionary                                  ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """
    print(f"{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BLUE}  AUTOMATED JUNIT TESTING SYSTEM - FIRST TIME SETUP{Colors.RESET}".center(88))
    print(f"{Colors.BLUE}{'='*80}{Colors.RESET}\n")
    
    config = {
        'HOMEWORKS_DIR': 'Homeworks',
        'TESTS_DIR': 'tests',
        'LIB_DIR': 'lib',
        'OUTPUT_DIR': 'output',
        'TEMP_DIR': 'temp_dir',
        'CURRENT_SUBMISSION_DIR': 'current_submission',
        'DONE_DIR': 'done',
        'JUNIT_JAR': 'junit-platform-console-standalone-1.14.1.jar',
        'JAVA_VERSION': '21',
        'ENABLE_PREVIEW': True,
        'GRADES_CSV': 'grades.csv',
        'CSV_HEADERS': ['Student Name', 'Matriculation Nr', 'Task 1', 'Task 2', 'Task 3', 'Comment'],
        'IGNORE_DIRS': ['_MACOSX', 'extracted', 'done']
    }
    
    # Step 1: Configure JDK Path
    print(f"{Colors.YELLOW}[1/3] Java JDK Configuration{Colors.RESET}")
    print("-" * 80)
    
    found_jdks = find_java_jdk()
    
    if found_jdks:
        print(f"Found {len(found_jdks)} Java JDK installation(s):\n")
        for idx, jdk_path in enumerate(found_jdks, 1):
            print(f"  {idx}. {jdk_path}")
        print(f"  {len(found_jdks) + 1}. Enter custom path")
        
        while True:
            choice = input(f"\nSelect JDK (1-{len(found_jdks) + 1}): ").strip()
            if choice.isdigit():
                choice_num = int(choice)
                if 1 <= choice_num <= len(found_jdks):
                    config['JDK_BIN_PATH'] = found_jdks[choice_num - 1]
                    print(f"{Colors.GREEN}Selected: {config['JDK_BIN_PATH']}{Colors.RESET}")
                    break
                elif choice_num == len(found_jdks) + 1:
                    custom_path = input("Enter JDK bin path: ").strip().strip('"')
                    if os.path.exists(os.path.join(custom_path, 'java.exe')):
                        config['JDK_BIN_PATH'] = custom_path
                        print(f"{Colors.GREEN}JDK path set to: {config['JDK_BIN_PATH']}{Colors.RESET}")
                        break
                    else:
                        print(f"{Colors.RED}Invalid path. java.exe not found.{Colors.RESET}")
            else:
                print(f"{Colors.RED}Invalid selection. Please enter a number.{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}No JDK installations found automatically.{Colors.RESET}")
        while True:
            jdk_path = input("Enter JDK bin path (e.g., C:\\Program Files\\Java\\jdk-21\\bin): ").strip().strip('"')
            if os.path.exists(os.path.join(jdk_path, 'java.exe')) and os.path.exists(os.path.join(jdk_path, 'javac.exe')):
                config['JDK_BIN_PATH'] = jdk_path
                print(f"{Colors.GREEN}JDK path set to: {config['JDK_BIN_PATH']}{Colors.RESET}")
                break
            else:
                print(f"{Colors.RED}Invalid path. java.exe and javac.exe not found.{Colors.RESET}")
    
    # Step 2: Select Test File
    print(f"\n{Colors.YELLOW}[2/3] Test File Selection{Colors.RESET}")
    print("-" * 80)
    
    # Create tests directory if it doesn't exist
    os.makedirs(config['TESTS_DIR'], exist_ok=True)
    
    # Find all Java test files
    test_files = [f for f in os.listdir(config['TESTS_DIR']) if f.endswith('.java')] if os.path.exists(config['TESTS_DIR']) else []
    
    if test_files:
        print(f"Found {len(test_files)} test file(s) in '{config['TESTS_DIR']}/' directory:\n")
        for idx, test_file in enumerate(test_files, 1):
            print(f"  {idx}. {test_file}")
        
        while True:
            choice = input(f"\nSelect test file (1-{len(test_files)}): ").strip()
            if choice.isdigit():
                choice_num = int(choice)
                if 1 <= choice_num <= len(test_files):
                    config['TEST_FILE'] = test_files[choice_num - 1]
                    print(f"{Colors.GREEN}Selected: {config['TEST_FILE']}{Colors.RESET}")
                    break
            print(f"{Colors.RED}Invalid selection. Please enter a number between 1 and {len(test_files)}.{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}No test files found in '{config['TESTS_DIR']}/' directory.{Colors.RESET}")
        print(f"Please add your JUnit test files to the '{config['TESTS_DIR']}/' directory.")
        test_file = input("Enter test file name (e.g., TestBank.java): ").strip()
        config['TEST_FILE'] = test_file
        print(f"{Colors.YELLOW}Test file set to: {config['TEST_FILE']}{Colors.RESET}")
        print(f"{Colors.YELLOW}Warning: Make sure to add this file to '{config['TESTS_DIR']}/' before running grading.{Colors.RESET}")
    
    # Step 3: Create Required Directories
    print(f"\n{Colors.YELLOW}[3/3] Creating Required Directories{Colors.RESET}")
    print("-" * 80)
    
    required_dirs = [
        config['HOMEWORKS_DIR'],
        os.path.join(config['HOMEWORKS_DIR'], config['DONE_DIR']),
        config['TESTS_DIR'],
        config['LIB_DIR'],
        config['OUTPUT_DIR']
    ]
    
    for directory in required_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"{Colors.GREEN}✓ Created: {directory}/{Colors.RESET}")
        else:
            print(f"  Already exists: {directory}/")
    
    # Save configuration
    print(f"\n{Colors.YELLOW}Saving configuration...{Colors.RESET}")
    save_config(config)
    
    print(f"{Colors.GREEN}{'='*80}{Colors.RESET}")
    print(f"{Colors.GREEN}Setup completed successfully!{Colors.RESET}".center(88))
    print(f"{Colors.GREEN}{'='*80}{Colors.RESET}\n")
    
    print("Next steps:")
    print(f"  1. Place student submissions in '{config['HOMEWORKS_DIR']}/' directory")
    print(f"  2. Ensure JUnit JAR is in '{config['LIB_DIR']}/' directory")
    print(f"  3. Ensure test file is in '{config['TESTS_DIR']}/' directory")
    print(f"  4. Run 'python app.py' to start grading\n")
    
    return config


# ============================================================================
#  Utility Functions
# ============================================================================

def extract_student_name(folder_name):
    """
    ╔══════════════════════════════════════════════════════════════════════╗
    ║  Extract Student Name                                                ║
    ╠══════════════════════════════════════════════════════════════════════╣
    ║  Extracts the student name from the folder name format:              ║
    ║  "FirstName LastName_ID_assignsubmission_file"                       ║
    ║                                                                      ║
    ║  Args:                                                               ║
    ║      folder_name (str): The folder name to parse                     ║
    ║                                                                      ║
    ║  Returns:                                                            ║
    ║      str: The student name (text before first underscore)            ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """
    return folder_name.split('_')[0]


def find_matriculation_number(folder_path):
    """
    ╔══════════════════════════════════════════════════════════════════════╗
    ║  Find Matriculation Number                                           ║
    ╠══════════════════════════════════════════════════════════════════════╣
    ║  Searches for an 8-digit matriculation number in the folder.        ║
    ║  First tries to find it with underscore prefix (_12345678),          ║
    ║  then without underscore if not found.                               ║
    ║                                                                      ║
    ║  Args:                                                               ║
    ║      folder_path (str): Path to the student's folder                 ║
    ║                                                                      ║
    ║  Returns:                                                            ║
    ║      str: The matriculation number, or None if not found             ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """
    pattern_with_underscore = r'_(\d{8})'
    pattern_without_underscore = r'\d{8}'
    
    # Try with underscore prefix first
    for item in os.listdir(folder_path):
        match = re.search(pattern_with_underscore, item)
        if match:
            return match.group(1)
    
    # Try without underscore
    for item in os.listdir(folder_path):
        match = re.search(pattern_without_underscore, item)
        if match:
            return match.group(0)
    
    return None


def determine_submission_type(folder_path):
    """
    ╔══════════════════════════════════════════════════════════════════════╗
    ║  Determine Submission Type                                           ║
    ╠══════════════════════════════════════════════════════════════════════╣
    ║  Analyzes the folder contents to determine submission type.          ║
    ║  Priority: Zipped files > Text files > Folders > Unknown             ║
    ║                                                                      ║
    ║  Args:                                                               ║
    ║      folder_path (str): Path to the student's folder                 ║
    ║                                                                      ║
    ║  Returns:                                                            ║
    ║      tuple: (submission_type, color_code)                            ║
    ║          - "Zipped file" (YELLOW)                                    ║
    ║          - "Text file" (GREEN)                                       ║
    ║          - "Folder" (BLUE)                                           ║
    ║          - "Unknown/Other file" (RED)                                ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        
        # Skip extracted folder from previous runs
        if item == 'extracted':
            continue
        
        # Check for zip files (highest priority)
        if item.endswith(('.zip', '.rar', '.7z')):
            return "Zipped file", Colors.YELLOW
        
        # Check for text files
        elif item.endswith('.txt'):
            return "Text file", Colors.GREEN
        
        # Check for folders
        elif os.path.isdir(item_path):
            return "Folder", Colors.BLUE
    
    return "Unknown/Other file", Colors.RED


def search_student_directory(folder_path, folder_name):
    """
    ╔══════════════════════════════════════════════════════════════════════╗
    ║  Search Student Directory                                            ║
    ╠══════════════════════════════════════════════════════════════════════╣
    ║  Analyzes a student's submission folder to extract:                  ║
    ║  - Student name                                                      ║
    ║  - Matriculation number                                              ║
    ║  - Submission type                                                   ║
    ║                                                                      ║
    ║  Args:                                                               ║
    ║      folder_path (str): Full path to student's folder                ║
    ║      folder_name (str): Name of the folder                           ║
    ║                                                                      ║
    ║  Returns:                                                            ║
    ║      dict: Student information containing:                           ║
    ║          - name: Student name                                        ║
    ║          - matriculation: Matriculation number                       ║
    ║          - submission_type: Type of submission                       ║
    ║          - color: Color code for display                             ║
    ║          - folder_path: Path to folder                               ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """
    student_name = extract_student_name(folder_name)
    matriculation_nr = find_matriculation_number(folder_path)
    submission_type, submission_color = determine_submission_type(folder_path)
    
    return {
        'name': student_name,
        'matriculation': matriculation_nr if matriculation_nr else 'Not found',
        'submission_type': submission_type,
        'color': submission_color,
        'folder_path': folder_path
    }


# ============================================================================
#  Java Compilation & Testing Functions
# ============================================================================

def verify_java_installation():
    """
    ╔══════════════════════════════════════════════════════════════════════╗
    ║  Verify Java Installation                                            ║
    ╠══════════════════════════════════════════════════════════════════════╣
    ║  Checks if Java executables (java.exe and javac.exe) exist at       ║
    ║  the configured JDK path.                                            ║
    ║                                                                      ║
    ║  Returns:                                                            ║
    ║      tuple: (java_exe_path, javac_exe_path) or (None, None) if fail ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """
    java_exe = os.path.join(Config['JDK_BIN_PATH'], "java.exe")
    javac_exe = os.path.join(Config['JDK_BIN_PATH'], "javac.exe")
    
    if not os.path.exists(java_exe) or not os.path.exists(javac_exe):
        print(f"{Colors.RED}Java executables not found at: {Config['JDK_BIN_PATH']}{Colors.RESET}")
        print("Please verify the JDK path in config/settings.json")
        return None, None
    
    return java_exe, javac_exe


def prepare_test_environment(temp_dir):
    """
    ╔══════════════════════════════════════════════════════════════════════╗
    ║  Prepare Test Environment                                            ║
    ╠══════════════════════════════════════════════════════════════════════╣
    ║  Copies test file and verifies JUnit JAR exists.                     ║
    ║                                                                      ║
    ║  Args:                                                               ║
    ║      temp_dir (str): Path to temporary directory                     ║
    ║                                                                      ║
    ║  Returns:                                                            ║
    ║      bool: True if setup successful, False otherwise                 ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """
    # Copy test file
    test_path = os.path.join(Config['TESTS_DIR'], Config['TEST_FILE'])
    if not os.path.exists(test_path):
        print(f"{Colors.RED}Test file not found: {test_path}{Colors.RESET}")
        return False
    
    shutil.copy2(test_path, os.path.join(temp_dir, Config['TEST_FILE']))
    print(f"Copied test file: {Config['TEST_FILE']}")
    
    # Verify JUnit JAR exists
    junit_jar_path = os.path.join(Config['LIB_DIR'], Config['JUNIT_JAR'])
    if not os.path.exists(junit_jar_path):
        print(f"{Colors.YELLOW}JUnit JAR not found: {junit_jar_path}{Colors.RESET}")
        print(f"Please download {Config['JUNIT_JAR']}")
        print(f"Place it in: {os.path.join(os.getcwd(), Config['LIB_DIR'])}")
        return False
    
    return True


def compile_java_files(temp_dir, current_submission_dir, javac_exe):
    """
    ╔══════════════════════════════════════════════════════════════════════╗
    ║  Compile Java Files                                                  ║
    ╠══════════════════════════════════════════════════════════════════════╣
    ║  Copies student files from current_submission to temp_dir,           ║
    ║  then compiles all Java files with JUnit in the classpath.           ║
    ║  Outputs .class files to a separate bin directory inside temp_dir.   ║
    ║                                                                      ║
    ║  Args:                                                               ║
    ║      temp_dir (str): Path to temporary directory                     ║
    ║      current_submission_dir (str): Path to current submission        ║
    ║      javac_exe (str): Path to javac executable                       ║
    ║                                                                      ║
    ║  Returns:                                                            ║
    ║      tuple: (success: bool, bin_dir: str)                            ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """
    # Copy student files from current_submission to temp_dir
    print(f"\nCopying files from {current_submission_dir} to {temp_dir}...")
    student_files = [f for f in os.listdir(current_submission_dir) if f.endswith('.java')]
    
    if not student_files:
        print("No Java files found in current_submission.")
        return False, None
    
    for file in student_files:
        src = os.path.join(current_submission_dir, file)
        dst = os.path.join(temp_dir, file)
        shutil.copy2(src, dst)
        print(f"  Copied: {file}")
    
    # Get all Java files in temp_dir (student files + test file)
    java_files = [f for f in os.listdir(temp_dir) if f.endswith('.java')]
    
    # Create bin directory for compiled classes
    bin_dir = os.path.join(temp_dir, 'bin')
    os.makedirs(bin_dir, exist_ok=True)
    
    print(f"\nCompiling {len(java_files)} Java file(s)...")
    print(f"Source files: {temp_dir}")
    print(f"Output directory: {bin_dir}")
    
    # Get JUnit JAR path from lib directory
    junit_jar = os.path.join(Config['LIB_DIR'], Config['JUNIT_JAR'])
    
    compile_cmd = [
        javac_exe, '-cp', f'{temp_dir};{junit_jar}',
        '-d', bin_dir,
        '--enable-preview', '--source', Config['JAVA_VERSION']
    ] + [os.path.join(temp_dir, f) for f in java_files]
    
    result = subprocess.run(compile_cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"{Colors.RED}Compilation failed:{Colors.RESET}")
        print(result.stderr)
        return False, None
    
    print(f"{Colors.GREEN}Compilation successful!{Colors.RESET}")
    return True, bin_dir


def execute_junit_tests(temp_dir, bin_dir, java_exe):
    """
    ╔══════════════════════════════════════════════════════════════════════╗
    ║  Execute JUnit Tests                                                 ║
    ╠══════════════════════════════════════════════════════════════════════╣
    ║  Runs JUnit tests on the compiled classes and displays results.      ║
    ║  Sets console to UTF-8 encoding for proper text display.            ║
    ║                                                                      ║
    ║  Args:                                                               ║
    ║      temp_dir (str): Path to temporary directory                     ║
    ║      bin_dir (str): Path to compiled classes directory               ║
    ║      java_exe (str): Path to java executable                         ║
    ║                                                                      ║
    ║  Returns:                                                            ║
    ║      bool: True if tests passed, False otherwise                     ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """
    print(f"\nRunning tests...")
    
    # Set console to UTF-8 encoding for proper text display
    subprocess.run(['chcp', '65001'], shell=True, capture_output=True)
    
    # Get JUnit JAR path from lib directory
    junit_jar = os.path.join(Config['LIB_DIR'], Config['JUNIT_JAR'])
    
    run_cmd = [
        java_exe, '-jar', junit_jar, 'execute',
        '--class-path', bin_dir, '--scan-class-path'
    ]
    result = subprocess.run(run_cmd, capture_output=True, text=True, encoding='utf-8')
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    # Check if tests passed
    if 'successful' in result.stdout.lower():
        print(f"\n{Colors.GREEN}✓ Tests passed!{Colors.RESET}")
        return True
    else:
        print(f"\n{Colors.RED}✗ Tests failed!{Colors.RESET}")
        return False


def run_junit_tests(temp_dir, current_submission_dir, student_info):
    """
    ╔══════════════════════════════════════════════════════════════════════╗
    ║  Run JUnit Tests (Main Orchestrator)                                 ║
    ╠══════════════════════════════════════════════════════════════════════╣
    ║  Orchestrates the entire testing process:                            ║
    ║  1. Verify Java installation                                         ║
    ║  2. Prepare test environment                                         ║
    ║  3. Compile Java files to separate bin directory                     ║
    ║  4. If compilation fails, prompt to recompile or continue            ║
    ║  5. Execute JUnit tests                                              ║
    ║                                                                      ║
    ║  Args:                                                               ║
    ║      temp_dir (str): Path to temporary compilation directory         ║
    ║      current_submission_dir (str): Path to current submission dir    ║
    ║      student_info (dict): Student information                        ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """
    try:
        # Step 1: Verify Java installation
        java_exe, javac_exe = verify_java_installation()
        if not java_exe or not javac_exe:
            return
        
        # Step 2: Prepare test environment
        if not prepare_test_environment(temp_dir):
            return
        
        # Step 3: Compile Java files with recompilation loop
        compilation_successful = False
        bin_dir = None
        
        while not compilation_successful:
            success, bin_dir = compile_java_files(temp_dir, current_submission_dir, javac_exe)
            
            if success:
                compilation_successful = True
            else:
                # Compilation failed - ask user what to do
                print(f"\n{Colors.YELLOW}{'='*80}{Colors.RESET}")
                print(f"{Colors.YELLOW}Compilation failed! You can now manually fix errors in:{Colors.RESET}")
                print(f"{Colors.BLUE}  {os.path.abspath(current_submission_dir)}{Colors.RESET}")
                print(f"{Colors.YELLOW}{'='*80}{Colors.RESET}")
                print("\nWhat would you like to do?")
                print("  1. Recompile (after manual fixes)")
                print("  2. Skip tests and continue to grading")
                
                choice = input("\nEnter your choice (1 or 2): ").strip()

                while choice not in ['1', '2']:
                    choice = input("Invalid choice. Please enter 1 or 2: ").strip()

                if choice == '1':
                    print(f"\n{Colors.BLUE}Retrying compilation...{Colors.RESET}")
                    # Clean bin directory before recompiling
                    bin_dir_path = os.path.join(temp_dir, 'bin')
                    if os.path.exists(bin_dir_path):
                        shutil.rmtree(bin_dir_path)
                    continue
                elif choice == '2':
                    print(f"\n{Colors.YELLOW}Skipping tests, proceeding to grading...{Colors.RESET}")
                    return
                else:
                    print(f"{Colors.RED}Invalid choice. Skipping tests...{Colors.RESET}")
                    return
        
        # Step 4: Execute tests
        execute_junit_tests(temp_dir, bin_dir, java_exe)
        
    except FileNotFoundError as e:
        print(f"{Colors.RED}Command not found: {str(e)}{Colors.RESET}")
        print("Please ensure Java JDK is installed.")
    except Exception as e:
        print(f"{Colors.RED}Error running tests: {str(e)}{Colors.RESET}")


# ============================================================================
#  File Processing Functions
# ============================================================================

def remove_package_declarations(directory):
    """
    ╔══════════════════════════════════════════════════════════════════════╗
    ║  Remove Package Declarations                                         ║
    ╠══════════════════════════════════════════════════════════════════════╣
    ║  Scans all Java files in the directory and removes package           ║
    ║  declarations to avoid compilation errors when compiling files       ║
    ║  outside their original package structure.                           ║
    ║                                                                      ║
    ║  Args:                                                               ║
    ║      directory (str): Path to directory containing Java files        ║
    ║                                                                      ║
    ║  Returns:                                                            ║
    ║      int: Number of files modified                                   ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """
    if not os.path.exists(directory):
        return 0
    
    files_modified = 0
    java_files = [f for f in os.listdir(directory) if f.endswith('.java')]
    
    for java_file in java_files:
        file_path = os.path.join(directory, java_file)
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Check for package declaration and remove it
            modified = False
            new_lines = []
            
            for line in lines:
                # Check if line contains package declaration
                stripped = line.strip()
                if stripped.startswith('package ') and stripped.endswith(';'):
                    print(f"  Removed package declaration from: {java_file}")
                    print(f"    {stripped}")
                    modified = True
                    # Skip this line (don't add to new_lines)
                    continue
                elif stripped.startswith("import ") and stripped.endswith(';'):
                    print(f"  Removed import declaration from: {java_file}")
                    print(f"    {stripped}")
                    modified = True
                    # Skip this line (don't add to new_lines)
                    continue
                else:
                    new_lines.append(line)
            
            # Write back if modified
            if modified:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
                files_modified += 1
        
        except Exception as e:
            print(f"{Colors.YELLOW}Warning: Could not process {java_file}: {str(e)}{Colors.RESET}")
    
    return files_modified


def extract_and_copy_java_files(folder_path, current_submission_dir):
    """
    ╔══════════════════════════════════════════════════════════════════════╗
    ║  Extract and Copy Java Files                                         ║
    ╠══════════════════════════════════════════════════════════════════════╣
    ║  Extracts zip files and recursively searches for Java files,         ║
    ║  copying them to the current_submission directory for review.        ║
    ║  Files are writable and can be manually edited if needed.            ║
    ║                                                                      ║
    ║  Args:                                                               ║
    ║      folder_path (str): Path to student's folder                     ║
    ║      current_submission_dir (str): Path to current submission dir    ║
    ║                                                                      ║
    ║  Returns:                                                            ║
    ║      str: Path to extracted folder for cleanup, or None              ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """
    for item in os.listdir(folder_path):
        if item.endswith(('.zip', '.rar', '.7z')):
            zip_path = os.path.join(folder_path, item)
            extract_path = os.path.join(folder_path, 'extracted')
            
            print(f"Extracting: {item}")
            
            # Extract zip file
            if item.endswith('.zip'):
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)
            
            # Search recursively for Java files
            java_files_found = 0
            
            for root, dirs, files in os.walk(extract_path):
                # Ignore _MACOSX directory
                if '_MACOSX' in root:
                    continue
                
                for file in files:
                    if file.endswith('.java'):
                        src_file = os.path.join(root, file)
                        dst_file = os.path.join(current_submission_dir, file)
                        
                        # Copy file (synchronous/blocking)
                        shutil.copy2(src_file, dst_file)
                        
                        # Remove read-only attribute
                        os.chmod(dst_file, 0o666)
                        
                        # Verify file was copied successfully
                        if os.path.exists(dst_file):
                            java_files_found += 1
                            print(f"  Copied: {file}")
                        else:
                            print(f"  {Colors.RED}Failed to copy: {file}{Colors.RESET}")
            
            print(f"Total Java files found and copied: {java_files_found}")
            
            if java_files_found > 0:
                print(f"{Colors.GREEN}Files extracted to: {current_submission_dir}{Colors.RESET}")
                
                # Remove package declarations from extracted files
                print(f"\nRemoving package declarations...")
                modified_count = remove_package_declarations(current_submission_dir)
                if modified_count > 0:
                    print(f"{Colors.GREEN}✓ Removed package declarations from {modified_count} file(s){Colors.RESET}")
                else:
                    print(f"  No package declarations found")
                
                print(f"{Colors.GREEN}You can review/edit files before compilation.{Colors.RESET}")
            
            return extract_path
    
    return None


def collect_grades():
    """
    ╔══════════════════════════════════════════════════════════════════════╗
    ║  Collect Grades from User                                            ║
    ╠══════════════════════════════════════════════════════════════════════╣
    ║  Prompts the user to enter grades for three tasks and a comment.     ║
    ║                                                                      ║
    ║  Returns:                                                            ║
    ║      tuple: (task1_grade, task2_grade, task3_grade, comment)         ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """
    print(f"\n{'='*80}")
    print("Enter grades for this student:")
    print(f"{'='*80}")
    
    task1_grade = ""
    task2_grade = ""
    task3_grade = ""
    comment = "0"
    
    while comment == "b" or comment == "0":
        while not (task1_grade.isdigit() and 0 <= int(task1_grade) <= 2):
            task1_grade = input("Grade for Task 1: ").strip()
        
        while not (task2_grade.isdigit() and 0 <= int(task2_grade) <= 2):
            task2_grade = input("Grade for Task 2: ").strip()

        while not (task3_grade.isdigit() and 0 <= int(task3_grade) <= 2):
            task3_grade = input("Grade for Task 3: ").strip()
    
        print("Enter an optional comment (type 'b' or '0' to re-enter grades):")
        comment = input("Comment: ").strip()
        if comment == "b" or comment == "0":
            task1_grade = ""
            task2_grade = ""
            task3_grade = ""
    
    return task1_grade, task2_grade, task3_grade, comment


def save_grades_to_csv(student_info, grades):
    """
    ╔══════════════════════════════════════════════════════════════════════╗
    ║  Save Grades to CSV                                                  ║
    ╠══════════════════════════════════════════════════════════════════════╣
    ║  Appends student grades to the CSV file. Creates file with headers   ║
    ║  if it doesn't exist.                                                ║
    ║                                                                      ║
    ║  Args:                                                               ║
    ║      student_info (dict): Student information                        ║
    ║      grades (tuple): (task1, task2, task3, comment)                  ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """
    csv_file = os.path.join(Config['OUTPUT_DIR'], Config['GRADES_CSV'])
    file_exists = os.path.exists(csv_file)
    
    with open(csv_file, 'a', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f, delimiter=';')
        
        # Write header if file is new
        if not file_exists:
            writer.writerow(['Student Name', 'Matriculation Nr', 'Task 1', 'Task 2', 'Task 3', 'Comment'])
        
        # Write student data
        writer.writerow([
            student_info['name'],
            student_info['matriculation'],
            grades[0],  # task1
            grades[1],  # task2
            grades[2],  # task3
            grades[3]   # comment
        ])
    
    print(f"{Colors.GREEN}Grades saved to {csv_file}{Colors.RESET}")


def move_to_done_folder(folder_path):
    """
    ╔══════════════════════════════════════════════════════════════════════╗
    ║  Move to Done Folder                                                 ║
    ╠══════════════════════════════════════════════════════════════════════╣
    ║  Moves the processed student folder to the 'done' directory to       ║
    ║  prevent reprocessing.                                               ║
    ║                                                                      ║
    ║  Args:                                                               ║
    ║      folder_path (str): Path to student's folder                     ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """
    done_dir = os.path.join(Config['HOMEWORKS_DIR'], Config['DONE_DIR'])
    if not os.path.exists(done_dir):
        os.makedirs(done_dir)
    
    folder_name = os.path.basename(folder_path)
    dest_path = os.path.join(done_dir, folder_name)
    
    # If destination exists, remove it first
    if os.path.exists(dest_path):
        shutil.rmtree(dest_path)
    
    shutil.move(folder_path, dest_path)
    print(f"{Colors.GREEN}Moved student folder to 'done' directory{Colors.RESET}")


def process_student_submission(student_info, temp_dir):
    """
    ╔══════════════════════════════════════════════════════════════════════╗
    ║  Process Student Submission (Main Orchestrator)                      ║
    ╠══════════════════════════════════════════════════════════════════════╣
    ║  Orchestrates the entire processing workflow for one student:        ║
    ║  1. Clear and setup temp & current_submission directories            ║
    ║  2. Extract and copy Java files to current_submission                ║
    ║  3. Run JUnit tests (copies to temp_dir for compilation)             ║
    ║  4. Collect grades from user                                         ║
    ║  5. Save grades to CSV                                               ║
    ║  6. Move folder to 'done'                                            ║
    ║  7. Cleanup temporary files                                          ║
    ║                                                                      ║
    ║  Args:                                                               ║
    ║      student_info (dict): Student information                        ║
    ║      temp_dir (str): Path to temporary compilation directory         ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """
    # Step 1: Setup directories
    current_submission_dir = Config['CURRENT_SUBMISSION_DIR']
    
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    
    if os.path.exists(current_submission_dir):
        shutil.rmtree(current_submission_dir)
    os.makedirs(current_submission_dir)
    
    print(f"\n{'='*80}")
    print(f"Processing: {student_info['name']} - {student_info['matriculation']}")
    print(f"{'='*80}")
    
    folder_path = student_info['folder_path']
    submission_type = student_info['submission_type']
    extract_path_to_clean = None
    
    # Step 2: Extract and copy Java files to current_submission
    if submission_type == "Zipped file":
        extract_path_to_clean = extract_and_copy_java_files(folder_path, current_submission_dir)
    elif submission_type == "Folder":
        # For folder submissions, search recursively for Java files
        print(f"Searching for Java files in folder submission...")
        java_files_found = 0
        
        for root, dirs, files in os.walk(folder_path):
            # Ignore _MACOSX and other system directories
            if '_MACOSX' in root or any(ignored in root for ignored in Config['IGNORE_DIRS']):
                continue
            
            for file in files:
                if file.endswith('.java'):
                    src = os.path.join(root, file)
                    dst = os.path.join(current_submission_dir, file)
                    
                    # Copy file
                    shutil.copy2(src, dst)
                    os.chmod(dst, 0o666)
                    java_files_found += 1
                    print(f"  Copied: {file}")
        
        print(f"Total Java files found and copied: {java_files_found}")
        
        if java_files_found > 0:
            print(f"{Colors.GREEN}Files copied to: {current_submission_dir}{Colors.RESET}")
            # Remove package declarations from copied files
            print(f"\nRemoving package declarations...")
            modified_count = remove_package_declarations(current_submission_dir)
            if modified_count > 0:
                print(f"{Colors.GREEN}✓ Removed package declarations from {modified_count} file(s){Colors.RESET}")
            else:
                print(f"  No package declarations found")
    
    # Step 3: Run JUnit tests if Java files were found
    if os.path.exists(current_submission_dir) and os.listdir(current_submission_dir):
        print(f"\n{'-'*80}")
        print("Running JUnit tests...")
        print(f"{'-'*80}")
        run_junit_tests(temp_dir, current_submission_dir, student_info)
    
    # Step 4: Collect grades from user
    grades = collect_grades()
    
    # Step 5: Save grades to CSV
    save_grades_to_csv(student_info, grades)
    
    # Step 6: Move folder to done directory
    move_to_done_folder(folder_path)
    
    # Step 7: Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        print(f"Cleared {temp_dir}")
    
    if os.path.exists(current_submission_dir):
        shutil.rmtree(current_submission_dir)
        print(f"Cleared {current_submission_dir}")
    
    if extract_path_to_clean and os.path.exists(extract_path_to_clean):
        shutil.rmtree(extract_path_to_clean)
        print(f"Cleared extracted folder: {extract_path_to_clean}")
    
    print()
    input("Press Enter to continue to next student...")


# ============================================================================
#  Main Application Functions
# ============================================================================

def scan_submissions():
    """
    ╔══════════════════════════════════════════════════════════════════════╗
    ║  Scan Submissions                                                    ║
    ╠══════════════════════════════════════════════════════════════════════╣
    ║  Scans the Homeworks directory and collects information about all    ║
    ║  student submissions (excluding the 'done' folder).                  ║
    ║                                                                      ║
    ║  Returns:                                                            ║
    ║      list: List of student information dictionaries                  ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """
    students_data = []
    
    for folder_name in os.listdir(Config['HOMEWORKS_DIR']):
        folder_path = os.path.join(Config['HOMEWORKS_DIR'], folder_name)
        
        # Skip the 'done' folder
        if folder_name.lower() == Config['DONE_DIR']:
            continue
        
        # Check if it's a directory
        if os.path.isdir(folder_path):
            student_info = search_student_directory(folder_path, folder_name)
            students_data.append(student_info)
    
    return students_data


def display_submissions_table(students_data):
    """
    ╔══════════════════════════════════════════════════════════════════════╗
    ║  Display Submissions Table                                           ║
    ╠══════════════════════════════════════════════════════════════════════╣
    ║  Displays a formatted table showing all student submissions with     ║
    ║  color-coded submission types.                                       ║
    ║                                                                      ║
    ║  Args:                                                               ║
    ║      students_data (list): List of student information               ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """
    print("\n" + "="*80)
    print(f"{'Student Name':<30} {'Matriculation Nr':<20} {'Submission Type':<30}")
    print("="*80)
    
    for student in students_data:
        color = student['color']
        print(f"{student['name']:<30} {student['matriculation']:<20} {color}{student['submission_type']:<30}{Colors.RESET}")
    
    print("="*80 + "\n")


def process_all_submissions(students_data):
    """
    ╔══════════════════════════════════════════════════════════════════════╗
    ║  Process All Submissions                                             ║
    ╠══════════════════════════════════════════════════════════════════════╣
    ║  Iterates through all student submissions and processes them one     ║
    ║  by one with user interaction.                                       ║
    ║                                                                      ║
    ║  Args:                                                               ║
    ║      students_data (list): List of student information               ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """
    temp_dir = Config['TEMP_DIR']
    
    # Create temp directory initially
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    # Process each student
    for student in students_data:
        process_student_submission(student, temp_dir)


def main():
    """
    ╔══════════════════════════════════════════════════════════════════════╗
    ║  Main Application Entry Point                                        ║
    ╠══════════════════════════════════════════════════════════════════════╣
    ║  Main workflow:                                                      ║
    ║  1. Load configuration (triggers init if first run)                  ║
    ║  2. Create necessary directories if they don't exist                 ║
    ║  3. Scan homework submissions                                        ║
    ║  4. Display submissions table                                        ║
    ║  5. Wait for user confirmation                                       ║
    ║  6. Process all submissions sequentially                             ║
    ║  7. Complete grading session                                         ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """
    # Set console to UTF-8 encoding for special characters
    subprocess.run(['chcp', '65001'], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Step 1: Load configuration (first-time setup if needed)
    load_config()
    
    # Step 2: Create necessary directories if they don't exist
    required_dirs = [
        Config['HOMEWORKS_DIR'],
        os.path.join(Config['HOMEWORKS_DIR'], Config['DONE_DIR']),
        Config['OUTPUT_DIR'],
        Config['LIB_DIR'],
        Config['TESTS_DIR']
    ]
    
    for directory in required_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"{Colors.GREEN}Created directory: {directory}/{Colors.RESET}")
    
    print(f"\n{'='*80}")
    print("  AUTOMATED JUNIT TESTING SYSTEM".center(80))
    print(f"{'='*80}\n")
    
    # Step 3: Scan submissions
    print("Scanning homework submissions...")
    students_data = scan_submissions()
    print(f"Found {len(students_data)} submission(s) to process.\n")
    
    if not students_data:
        print(f"{Colors.YELLOW}No submissions found to process.{Colors.RESET}")
        print(f"All submissions may already be in the '{Config['DONE_DIR']}' folder.")
        return
    
    # Step 4: Display table
    display_submissions_table(students_data)
    
    # Step 5: Wait for confirmation
    input("Press Enter to start grading submissions...")
    
    # Step 6: Process all submissions
    process_all_submissions(students_data)
    
    # Step 7: Complete
    print(f"\n{'='*80}")
    print(f"{Colors.GREEN}Grading session completed!{Colors.RESET}".center(90))
    print(f"Results saved to: {os.path.join(Config['OUTPUT_DIR'], Config['GRADES_CSV'])}")
    print(f"{'='*80}\n")


# ============================================================================
#  Application Entry Point
# ============================================================================

if __name__ == "__main__":
    main()
