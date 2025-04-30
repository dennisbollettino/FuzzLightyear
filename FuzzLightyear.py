import argparse
import re
import sys
import random
import string
import requests

""" Function manages the mutation loop and login attempts to the target URL"""
def fuzz(seed, regex, max_attempts, url, username):
    # maybe we could have an input flag that lets the user alternate between the different mutation strategies we talked about
    pass

""" Function that handles one mutation """
def mutate(seed, regex):
    while True: # Loop until a valid candidate is found
        pwd = list(seed) # Convert seed to a list of characters for mutation

        mutation_type = random.choice(['sub', 'insert', 'delete', 'swap', 'case']) # Randomly select a mutation type

        if mutation_type == 'sub': # Chooses a random character and substitutes it with a random character of the same type
            idx = random.randrange(len(pwd))
            old = pwd[idx]
            if old.islower():
                pwd[idx] = random.choice(string.ascii_lowercase)
            elif old.isupper():
                pwd[idx] = random.choice(string.ascii_uppercase)
            elif old.isdigit():
                pwd[idx] = random.choice(string.digits)
            else:
                pwd[idx] = random.choice(string.punctuation)

        elif mutation_type == 'insert': # Inserts a random character at a random position
            char = random.choice(string.ascii_letters + string.digits + string.punctuation)
            idx = random.randrange(len(pwd) + 1)
            pwd.insert(idx, char)

        elif mutation_type == 'delete' and len(pwd) > 1: # Deletes a random character from the password
            idx = random.randrange(len(pwd))
            del pwd[idx]

        elif mutation_type == 'swap' and len(pwd) >= 2: # Swaps two adjacent characters in the password
            i = random.randrange(len(pwd) - 1)
            pwd[i], pwd[i+1] = pwd[i+1], pwd[i]

        elif mutation_type == 'case': # Swaps the case of a random character in the password
            idx = random.randrange(len(pwd))
            pwd[idx] = pwd[idx].swapcase()

        candidate = ''.join(pwd) # Convert list back to string

        if re.fullmatch(regex, candidate): # Returns the candidate if it matches the regex pattern
            return candidate

""" Function to check whether a string is a valid regex pattern """
def valid_regex(value):
    try:
        re.compile(value)
        return value
    except re.error:
        raise argparse.ArgumentTypeError(f"Invalid regex pattern: {value}")

""" Function to check whether a string is a valid URL """
def valid_url(value):
    if not value.startswith(('http://', 'https://')):
        raise argparse.ArgumentTypeError("URL must start with http:// or https://")
    return value

""" Function to parse command line arguments """
def parse_args():
    parser = argparse.ArgumentParser(
        description=" Fuzz Lightyear: To Login and Beyond!"
    )

    parser.add_argument('--url', required=True, type=valid_url,
                        help="Target login endpoint (e.g. http://localhost:5000/login)")
    parser.add_argument('--username', required=True,
                        help="Username to test")
    parser.add_argument('--seed', required=True, type=str, default="Password123!",
                        help="Seed password to mutate")
    parser.add_argument('--regex', required=True, type=valid_regex,
                        help="Regex pattern password must satisfy")
    parser.add_argument('--max-time', type=int, default=60,
                        help="Maximum execution time in seconds")
    parser.add_argument('--max-attempts', type=int, default=500,
                        help="Maximum number of password attempts")

    args = parser.parse_args()

    # Custom post-checks
    if args.max_time <= 0:
        parser.error("max-time must be a positive integer")

    if args.max_attempts <= 0:
        parser.error("max-attempts must be a positive integer")

    return args

""" Main function to run the script """
def main():
    args = parse_args()

    # Placeholder for the main logic of the script
    """
    print(f"URL: {args.url}")
    print(f"Username: {args.username}")
    print(f"Seed Password: {args.seed}")
    print(f"Regex Pattern: {args.regex}")
    print(f"Max Time: {args.max_time} seconds")
    print(f"Max Attempts: {args.max_attempts}")
    """

    # Call fuzz function with parsed arguments
    #fuzz(args.seed, args.regex, args.max_attempts, args.url, args.username)

if __name__ == "__main__":
    main()