import os
import subprocess
import sys
import glob

def main():
    """
    Finds and runs all test scripts in the current directory.
    """
    # Define color codes for output
    GREEN = '\033[92m'
    RED = '\033[91m'
    RESET = '\033[0m'

    # Get the directory where this script is located
    test_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct the absolute path to the venv python interpreter
    project_root = os.path.dirname(test_dir)
    python_executable = os.path.join(project_root, 'venv', 'bin', 'python3')

    if not os.path.exists(python_executable):
        print(f"{RED}ERROR: Python interpreter not found at '{python_executable}'{RESET}")
        sys.exit(1)

    # Find all python files in the test directory, excluding this script
    this_script_name = os.path.basename(__file__)
    test_files = [
        f for f in glob.glob(os.path.join(test_dir, '*.py'))
        if os.path.basename(f) != this_script_name
    ]

    if not test_files:
        print("No test files found to run.")
        sys.exit(0)

    print(f"Found {len(test_files)} test file(s) to run...")
    print("-" * 40)

    failed_tests = []
    passed_tests = []

    for test_file in sorted(test_files):
        test_name = os.path.basename(test_file)
        print(f"Running test: {test_name}...")
        
        # Prepare environment variables for the subprocess, specifically setting PYTHONPATH
        env = os.environ.copy()
        env['PYTHONPATH'] = project_root
        
        try:
            # Run the test script as a subprocess using the venv python
            result = subprocess.run(
                [python_executable, test_file],
                capture_output=True,
                text=True,
                check=False,  # Do not raise exception on non-zero exit code
                env=env # Pass the modified environment
            )

            # Print stdout and stderr for debugging purposes
            if result.stdout:
                print("---" + " STDOUT ---" + "\n" + result.stdout)
            if result.stderr:
                print("---" + " STDERR ---" + "\n" + result.stderr)

            # Check the return code to determine pass/fail
            if result.returncode == 0:
                print(f"{GREEN}---> PASS: {test_name}{RESET}\n")
                passed_tests.append(test_name)
            else:
                print(f"{RED}---> FAIL: {test_name} (Exit code: {result.returncode}){RESET}\n")
                failed_tests.append(test_name)
        
        except Exception as e:
            print(f"{RED}---> ERROR: An exception occurred while running {test_name}: {e}{RESET}\n")
            failed_tests.append(test_name)
        
        print("-" * 40)

    # Print summary
    print("\n--- TEST SUMMARY ---")
    print(f"{GREEN}Passed: {len(passed_tests)}{RESET}")
    print(f"{RED}Failed: {len(failed_tests)}{RESET}")

    if failed_tests:
        print("\nFailed tests:")
        for test in failed_tests:
            print(f"- {test}")
        sys.exit(1)
    else:
        print(f"\n{GREEN}All tests passed successfully!{RESET}")
        sys.exit(0)

if __name__ == "__main__":
    main()
