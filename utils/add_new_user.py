#!/usr/bin/env python3
import os
import yaml
import bcrypt
import getpass
import re
import sys

# Ensure the script is running from the project root
if not os.path.exists('user/accounts'):
    print("Error: This script must be run from the root directory of the CMS project.", file=sys.stderr)
    sys.exit(1)

def is_valid_username(username):
    """Check if the username is valid (alphanumeric, no spaces)."""
    return re.match(r'^[a-zA-Z0-9_-]+$', username)

def prompt_for_data():
    """Interactively prompts the user for new user data."""
    print("--- Create a New CMS User ---")
    
    # --- Username ---
    while True:
        username = input("Enter username (e.g., 'johnsmith'): ").strip()
        if not username:
            print("Username cannot be empty.")
        elif not is_valid_username(username):
            print("Invalid username. Use only letters, numbers, underscores, or hyphens.")
        elif os.path.exists(f'user/accounts/{username}.yaml'):
            print(f"Error: User '{username}' already exists.")
        else:
            break

    # --- Full Name ---
    fullname = input("Enter full name (e.g., 'John Smith'): ").strip()
    if not fullname:
        fullname = username

    # --- Email ---
    email = input("Enter email address (e.g., 'john.smith@example.com'): ").strip()

    # --- Title ---
    title = input("Enter user title (e.g., 'Content Editor'): ").strip()
    if not title:
        title = "User"

    # --- Access Level ---
    print("\nSelect access level:")
    print("  1. Site Administrator (Full access)")
    print("  2. Standard User (Site login only)")
    while True:
        choice = input("Enter choice (1 or 2): ").strip()
        if choice in ['1', '2']:
            break
        print("Invalid choice. Please enter 1 or 2.")
    
    if choice == '1':
        access = {'admin': {'login': True}, 'site': {'login': True}}
    else:
        access = {'site': {'login': True}}

    # --- Password ---
    while True:
        password = getpass.getpass("Enter password (will not be shown): ")
        if not password:
            print("Password cannot be empty.")
            continue
        password_confirm = getpass.getpass("Confirm password: ")
        if password == password_confirm:
            break
        print("Passwords do not match. Please try again.")
            
    return username, {
        'state': 'enabled',
        'fullname': fullname,
        'email': email,
        'title': title,
        'access': access,
        'hashed_password': bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    }

def main():
    """Main function to run the script."""
    try:
        username, user_data = prompt_for_data()
        
        output_path = f'user/accounts/{username}.yaml'
        
        with open(output_path, 'w') as f:
            yaml.dump(user_data, f, default_flow_style=False, sort_keys=False)
            
        print(f"\nSuccess! User '{username}' created at '{output_path}'")
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
