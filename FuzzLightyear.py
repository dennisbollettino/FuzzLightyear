import argparse
import re
import random
import string
import time
import requests
import json

# DEFAULT_REGEX = "^[A-Za-z0-9!?]{6,11}$"
PASSWORD_CACHE = set()

def fuzz(seed, regex, max_attempts, max_time, url, username, fuzz_type, iterations, verbose):
    """
    Main fuzzer driver function

    Args:
        seed (string): seed password for fuzzer
        regex (string): regular expression for password format
        max_attempts (int): maximum attempts before aborting (0: infinite)
        max_time (int): maximum time (in seconds) before time-out (0: infinite)
        url (string): target url
        username (string): target username
        fuzz_type (int): Fuzzing mode (0: Simple, 1: Iterative, 2: Complex)
        iterations (int): Number of iterations to run on this seed (for testing)
        verbose (bool): Suppress per-attempt output during fuzzing
    Returns:
        Tuple(string, int, int): Returns a tuple of the generated password (if any), attempts taken, and time elapsed
    """

    start_time = time.time() # Start time-out timer
    curr_attempt = 0 # current attempt
    past_mutation = seed # setting first iteration of past_mutation to seed
    s = requests.Session()

    while(True):
        output = mutation_handler(seed, past_mutation, regex, fuzz_type, curr_attempt) 
        generated_pass = output[0]
        past_mutation = output[1]
        curr_attempt += 1

        if verbose:
            print("{}{}{}{}".format("Attempt: ", curr_attempt, ", produced: ", generated_pass))

            # Submit Attempt

        payload = {"username": username, "password": generated_pass}
        r = s.post(url, data=json.dumps(payload), headers={"Content-Type": "application/json"})
        
        if(r.status_code == 404): # URL not found, abort process
            print("\nError 404: URL not found")
            if verbose:
                print("Total Execution Time: {:.2f} seconds".format(time.time() - start_time))
                print("Total Attempts: {}".format(curr_attempt))
                s.close()
            exit(1)

        if r.status_code == 200: # Password successfully discovered
            if iterations == 1 or verbose:
                print("{}{}".format("\nSuccess! Password is: ", generated_pass))
                print("Total Execution Time: {:.2f} seconds".format(time.time() - start_time))
                print("Total Attempts: {}".format(curr_attempt))
            s.close()
            return generated_pass, curr_attempt, max((time.time() - start_time), 0)

        PASSWORD_CACHE.add(generated_pass) # Add last guess to hash table to prevent repeat attempts

        if curr_attempt % 6324: # Clear hash table after every 6324 attempts
            PASSWORD_CACHE.clear()

        
        elapsed_time = time.time() - start_time
        if(max_time != 0 and (time.time()-start_time) > max_time): # Check time-out timer
            if verbose:
                print("\nMax Time Reached. Aborting Process")
                print("Total Execution Time: {:.2f} seconds".format(time.time() - start_time))
                print("Total Attempts: {}".format(curr_attempt))
            s.close()
            return None, curr_attempt, max((time.time() - start_time), 0)

        if(max_attempts != 0 and curr_attempt > max_attempts): # Check attempt counter
            if verbose:
                print("\nMax Attempts Reached. Aborting Process")
                print("Total Execution Time: {:.2f} seconds".format(time.time() - start_time))
                print("Total Attempts: {}".format(curr_attempt))
            s.close()
            return None, curr_attempt, max((time.time() - start_time), 0)


def mutation_handler(seed, past_mutation, regex, fuzz_type, curr_attempt):
    """
    Mutation handler function

    Args:
        seed (string): seed password for fuzzer
        past_mutation (string): Last password generated
        regex (string): regular expression for password format
        fuzz_type (int): Fuzzing mode (0: Simple, 1: Iterative, 2: Complex)
        curr_attempt (int): Current attempt number
    Returns:
        Tuple(string, string): First value is generated password to attempt, Second value is the past attempt
    """

    if fuzz_type == 0: # Simple mutation chosen, seed used in all runs
        generated_pass = mutate(seed, regex, 0)

    if fuzz_type == 1: # Iterative mutation chosen, past_mutation used as seed for next run. Resets after every 25 attempts
        if curr_attempt % 25 == 0:
            past_mutation = seed
        generated_pass = mutate(past_mutation, regex, 0)
        past_mutation = generated_pass

    if fuzz_type == 2: # Complex mutation chosen, 2 mutates per run. Resets after every 10 attempts
        if curr_attempt % 10 == 0:
            past_mutation = seed
        generated_pass = mutate(past_mutation, regex, 1)
        generated_pass = mutate(generated_pass, regex, 1)
        past_mutation = generated_pass
    
    return [generated_pass, past_mutation]

def mutate(seed, regex, complex_mode):
    """
    Main mutation generator function

    Args:
        seed (string): seed password for fuzzer
        regex (string): regular expression for password format
        complex_mode (bool): True if complex mode is used
    Returns:
        string: unique mutated password
    """

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
        if re.fullmatch(regex, candidate) and (complex_mode or candidate not in PASSWORD_CACHE): # Returns the candidate if it matches the regex pattern and isn't in the hash table
            return candidate


def valid_regex(value):
    """
    Function to check whether a string is a valid regex pattern

    Args:
        value (string): Regex pattern to be tested for validity
    Returns:
        string: Valid regex pattern
    Raises:
        ArgumentTypeError: If value is invalid regex pattern
    """

    try:
        re.compile(value)
        return value
    except re.error:
        raise argparse.ArgumentTypeError(f"Invalid regex pattern: {value}")


def valid_url(value):
    """
    Function to check whether a string is a valid URL

    Args:
        value (string): url to be tested for validity
    Returns:
        string: Valid url
    Raises:
        ArgumentTypeError: If value is invalid url
    """

    if not value.startswith(('http://', 'https://')):
        raise argparse.ArgumentTypeError("URL must start with http:// or https://")
    return value


def parse_args():
    """
    Function to parse command line arguments

    Returns:
        arguments supplied by user
    Raises:
        parser_error: If arguments are invalid
    """
    parser = argparse.ArgumentParser(
        description=" Fuzz Lightyear: To Login and Beyond!"
    )

    parser.add_argument('--url', required=True, type=valid_url,
                        help="Target login endpoint (e.g. http://localhost:5000/login)")
    parser.add_argument('--username', required=True,
                        help="Username to test")
    parser.add_argument('--seed', required=True, type=str, default="Password123!",
                        help="Seed password to mutate")
    parser.add_argument('--regex', type=valid_regex, default="^[A-Za-z0-9!?]{6,11}$",
                        help="Regex pattern password must satisfy")
    parser.add_argument('--max-time', type=int, default=60,
                        help="Maximum execution time in seconds")
    parser.add_argument('--max-attempts', type=int, default=500,
                        help="Maximum number of password attempts")
    parser.add_argument('--fuzz-type', type=int, default=0,
                        help="Fuzzing Type (0 - Simple, 1 - Iterative, 2 - Complex)")
    parser.add_argument('--iterations', type=int, default = 1,
                        help="Number of iterations to run on this seed (for testing)")
    parser.add_argument('--verbose', action='store_true', default=False,
                    help="Suppress per-attempt output during fuzzing")
    
    args = parser.parse_args()

    # Custom post-checks
    if args.max_time < 0:
        parser.error("max-time must be a positive integer")
    if args.max_attempts < 0:
        parser.error("max-attempts must be a positive integer")
    if args.fuzz_type < 0 or args.fuzz_type > 2:
        parser.error("Fuzz Type must be 0, 1, or 2")
    if not re.fullmatch(args.regex, args.seed):
        parser.error(f"Seed must full match regex: {args.regex}")
    return args


""" Main function to run the script """
def main():
    args = parse_args()
    # Placeholder for the main logic of the script
    print(r"""
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
    print(f"Regex Pattern: {args.regex}")
    print(f"Max Time: {args.max_time} seconds")
    print(f"Max Attempts: {args.max_attempts}")
    print(f"Fuzz Type: {args.fuzz_type}")
    print(f"Iterations: {args.iterations}")
    print(f"Verbose: {args.verbose}")
    print("\n\nFuzz Lightyear is ready to launch!\n")
    input("\n\nPress enter when you are ready to begin fuzzing!")

    total_time = 0
    total_time_success = 0
    total_attempts = 0
    total_attempts_success = 0
    success_count = 0
    failure_count = 0


    for i in range(args.iterations):
        if args.iterations > 1:
            print(f"\n--- Fuzzing Iteration {i + 1} ---")
        password, attempts, elapsed = fuzz(args.seed, args.regex, args.max_attempts, args.max_time, args.url, args.username, args.fuzz_type, args.iterations, args.verbose)
        total_attempts += attempts
        total_time += elapsed
        if args.iterations > 1 and password != None and not args.verbose:
            total_attempts_success += attempts
            total_time_success += elapsed
            success_count += 1
            print(f"Iteration {i + 1} succeeded in {elapsed:.2f} seconds after {attempts} attempts with password: {password}")
        elif args.iterations > 1 and password == None:
            failure_count += 1
            print(f"Iteration {i + 1} failed after {elapsed:.2f} seconds with {attempts} attempts")
            
    if args.iterations > 1:
        print("\n=== Summary ===")
        avg_time = total_time / args.iterations
        avg_time_success = total_time_success / success_count if success_count > 0 else 0
        avg_attempts = total_attempts / args.iterations
        avg_attempts_success = total_attempts_success / success_count if success_count > 0 else 0
        print(f"Total Average Time: {avg_time:.2f} seconds")
        print(f"Total Average Attempts: {avg_attempts:.2f}")
        print(f"Average Time for Successful Iterations: {avg_time_success:.2f} seconds")
        print(f"Average Attempts for Successful Iterations: {avg_attempts_success:.2f}")
        print(f"Successes: {success_count}")
        print(f"Failures: {failure_count}")

if __name__ == "__main__":
    main()