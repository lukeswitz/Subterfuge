#!/usr/bin/env python3

import re
import idna
import os
import subprocess
import sys
import time
import argparse
from tqdm import tqdm  # Import tqdm for progress bar

print("""
              8        o                d'b                      
              8        8                8                        
.oPYo. o    o 8oPYo.  o8P .oPYo. oPYo. o8P  o    o .oPYo. .oPYo. 
Yb..   8    8 8    8   8  8oooo8 8  `'  8   8    8 8    8 8oooo8 
  'Yb. 8    8 8    8   8  8.     8      8   8    8 8    8 8.     
`YooP' `YooP' `YooP'   8  `Yooo' 8      8   `YooP' `YooP8 `Yooo' 
:.....::.....::.....:::..::.....:..:::::..:::.....::....8 :.....:
:::::::::::::::::::::::::::::::::::::::::::::::::::::ooP'.:::::::
:::::::::::::::::::::::::::::::::::::::::::::::::::::...:::::::::
""")

total_subdomains = set()
total_permutations = 0  # Initialize total permutations counter

def run_command(command, env=None, timeout=300):
    """Run a shell command."""
    result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True, env=env, timeout=timeout)
    return result.stdout.strip()

def set_go_env():
    go_path = run_command("go env GOPATH")
    if not go_path:
        go_path = os.path.expanduser("~/go")
        os.environ["GOPATH"] = go_path
        run_command(f"go env -w GOPATH={go_path}")
    
    go_bin_path = os.path.join(go_path, "bin")
    if go_bin_path not in os.environ["PATH"]:
        os.environ["PATH"] += os.pathsep + go_bin_path

def install_tool(tool_name, install_command, env=None):
    """Install a specific tool."""
    try:
        run_command(f"which {tool_name}", env=env)
    except subprocess.CalledProcessError:
        run_command(install_command, env=env)

def check_and_install_tools():
    """Check for the presence of required tools and install them if not present."""
    set_go_env()
    tools_install_commands = {
        "alterx": "go install github.com/projectdiscovery/alterx/cmd/alterx@latest",
        "gotator": "go install github.com/Josue87/gotator@latest",
        "altdns": "pip install -q py-altdns",
        "puredns": "go install github.com/d3mondev/puredns/v2@latest",
        "ripgen": "cargo install ripgen",
        "lepus": "pip install -q lepus",
        "dnsgen": "python -m pip install -q dnsgen",
        "httpx": "go install github.com/projectdiscovery/httpx/cmd/httpx@latest"
    }
    env = os.environ.copy()
    for tool, install_command in tools_install_commands.items():
        install_tool(tool, install_command, env=env)

def is_valid_domain(domain):
    """Validate if the domain is in a proper format."""
    if not domain:
        return False
    try:
        # Convert the domain to Punycode
        punycode_domain = idna.encode(domain).decode('ascii')
    except idna.IDNAError:
        return False
    
    regex = re.compile(
        r'^(?=.{1,253}$)(?!-)[A-Za-z0-9-]{1,63}(?<!-)'  # Subs and hosts
        r'(\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))*'           # Additional subdomains
        r'\.[A-Za-z]{2,}$'                             # TLDs
    )
    return re.match(regex, punycode_domain) is not None
    

def run_tool(tool, command):
    global total_subdomains, total_permutations
    print(f"Running {tool}...")
    try:
        run_command(command, timeout=1800)  # Set a 30-minute timeout for each tool
        permutations_file = command.split()[-1]
        
        # Read permutations and update counts
        with open(permutations_file, 'r') as file:
            result = {line.strip() for line in file if line.strip()}
        
        new_subdomains = result - total_subdomains
        new_count = len(new_subdomains)
        total_subdomains.update(new_subdomains)
        total_permutations = len(total_subdomains)
        print(f"{tool} finished - {new_count} new permutations added - Total Permutations: {total_permutations}")
    except subprocess.CalledProcessError as e:
        print(f"Error running {tool}: {e}")
    except subprocess.TimeoutExpired as e:
        print(f"Timeout running {tool}: {e}")


def check_live_subdomains(subdomains_file, output_file, chunk_size=100):
    """Check which subdomains are live using httpx with a progress bar."""
    print("")
    try:
        # Read subdomains from the file
        with open(subdomains_file, 'r') as file:
            subdomains = [line.strip() for line in file if is_valid_domain(line.strip())]

        total_count = len(subdomains)
        if total_count == 0:
            print("No subdomains to check.")
            return set()

        live_subdomains = set()
        temp_output_file = output_file + ".temp"

        # Check subdomains in chunks
        with tqdm(total=len(total_subdomains), desc="Analyzing subdomains", unit="subdomain") as pbar:  # Use total_permutations
            for i in range(0, total_count, chunk_size):
                chunk = subdomains[i:i + chunk_size]
                chunk_file = f"{subdomains_file}.chunk"
                
                # Write the chunk to a temporary file
                with open(chunk_file, 'w') as chunk_f:
                    chunk_f.write('\n'.join(chunk) + '\n')

                # Execute httpx command with -l and -o options for the chunk
                command = f"httpx -silent -fc 404 -l {chunk_file} -o {temp_output_file}"
                result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=900)

                if result.returncode != 0:
                    print(f"Error running httpx: {result.stderr}")
                    continue

                # Read the live subdomains from the temp output file
                with open(temp_output_file, 'r') as temp_f:
                    for line in temp_f:
                        stripped_subdomain = re.sub(r'^https?://', '', line.strip())
                        live_subdomains.add(stripped_subdomain)

                pbar.update(len(chunk))

                # Clean up temporary chunk file
                os.remove(chunk_file)

        # Write the live subdomains to the output file
        with open(output_file, 'w') as file:
            for subdomain in live_subdomains:
                file.write(f"{subdomain}\n")

        print(f"\n[*] Total of {len(live_subdomains)} live subdomains.")
        print(f"Live subdomains saved to {output_file}")

        return live_subdomains

    except subprocess.CalledProcessError as e:
        print(f"Error running httpx: {e}")
        return set()
    except subprocess.TimeoutExpired as e:
        print(f"Timeout running httpx: {e}")
        return set()


def count_lines(file_path):
    return int(subprocess.check_output(['wc', '-l', file_path]).split()[0])

def main(domain):
    start_time = time.time()
    print(f"Discovery initiated for {domain}\n")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_folder = os.path.join(base_dir, f"results/{domain}")
    os.makedirs(output_folder, exist_ok=True)
    
    subdomain_file = os.path.join(base_dir, f"SubdomainTool/results/{domain}/subdomains.txt")
    live_subdomains_file = os.path.join(base_dir, f"SubdomainTool/results/{domain}/live_subdomains.txt")
    patterns_file = os.path.join(base_dir, "patterns.txt")  # Corrected path to the root level

    check_and_install_tools()

    # Check if either subdomains.txt or live_subdomains.txt exists
    if not os.path.exists(subdomain_file) and not os.path.exists(live_subdomains_file):
        print(f"No subdomain file found at {subdomain_file} or {live_subdomains_file}")
        return
    
    # Use the appropriate file for subdomain processing, prioritize live_subdomains_file
    if os.path.exists(live_subdomains_file):
        file_to_use = live_subdomains_file
        print(f"Using live_subdomains_file: {live_subdomains_file}")
    else:
        file_to_use = subdomain_file
        print(f"Using subdomain_file: {subdomain_file}")

    subdomain_count = count_lines(file_to_use)
    pattern_count = count_lines(patterns_file)
    print(f"Number of subdomains: {subdomain_count}")
    print(f"Number of patterns: {pattern_count}\n")

    tools = {
        "alterx": f"alterx -l {file_to_use} -p {patterns_file} -ms 15 -o {output_folder}/alterx_permutations.txt",
        "gotator": f"gotator -sub {file_to_use} -perm {patterns_file} -depth 0 -numbers 0 -mindup -adv -md > {output_folder}/gotator_permutations.txt",
        "dnsgen": f"dnsgen {file_to_use} > {output_folder}/dnsgen_permutations.txt",
        "ripgen": f"ripgen -d {file_to_use} > {output_folder}/ripgen_permutations.txt",
        #"lepus": f"lepus.py --permutate -pw {patterns_file} -o {output_folder}/lepus_permutations.txt {file_to_use}"
    }

    for tool, command in tools.items():
        run_tool(tool, command)

    # Combine all permutations into one file
    all_permutations_file = os.path.join(output_folder, "all_permutations.txt")
    with open(all_permutations_file, 'w') as outfile:
        for tool, _ in tools.items():
            permutations_file = os.path.join(output_folder, f"{tool}_permutations.txt")
            if os.path.exists(permutations_file):
                with open(permutations_file, 'r') as infile:
                    for line in infile:
                        outfile.write(line)

    # Check live subdomains using httpx
    live_subdomains_file = os.path.join(output_folder, "live_subdomains.txt")
    check_live_subdomains(all_permutations_file, live_subdomains_file)

    end_time = time.time()
    runtime = end_time - start_time
    
    # Print the results
    total_live_count = len(open(live_subdomains_file).readlines())  # Line to print live subdomains count
    print(f"\n[+] Total Live Subdomains: {total_live_count}")
    print(f"Runtime: {int(runtime // 3600)}:{int((runtime % 3600) // 60)}:{int(runtime % 60)} (hh:mm:ss).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Subdomain enumeration script")
    parser.add_argument("domain", help="The domain to enumerate subdomains for")
    args = parser.parse_args()

    main(args.domain)
