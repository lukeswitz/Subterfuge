#!/usr/bin/env python3

import subprocess
import os
import argparse
import urllib.request
import time
import re
from tqdm import tqdm
import shutil
import idna
import glob

print("""
            _                                 
           | |     _                          
  ___ _   _| |__ _| |_ _____  ____ ____ _____ 
 /___) | | |  _ (_   _) ___ |/ ___) ___|____ |
|___ | |_| | |_) )| |_| ____| |  | |   / ___ |
(___/|____/|____/  \__)_____)_|  |_|   \_____|
                                             
""")

total_subdomains = set()

def run_command(command, env=None, timeout=300):
    """Run a shell command and capture output."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True, env=env, timeout=timeout)
    if result.returncode != 0:
        print(f"Error running command: {result.stderr}")
        raise subprocess.CalledProcessError(result.returncode, command, output=result.stdout, stderr=result.stderr)
    return result.stdout.strip()

def get_go_path():
    """Retrieve GOPATH using go env."""
    try:
        gopath = run_command("go env GOPATH")
        return gopath
    except subprocess.CalledProcessError:
        return os.path.expanduser("~/go")

def install_golang():
    """Install Go if not already installed."""
    try:
        run_command("go version")
    except subprocess.CalledProcessError:
        run_command("wget https://golang.org/dl/go1.16.5.linux-amd64.tar.gz")
        run_command("tar -C $HOME -xzf go1.16.5.linux-amd64.tar.gz")
        os.environ["PATH"] += os.pathsep + os.path.expanduser("~/go/bin")

def install_tool(tool_name, install_command, env=None):
    """Install a specific tool if it is not already installed."""
    try:
        run_command(f"which {tool_name}", env=env)
        print(f"{tool_name} is already installed.")
    except subprocess.CalledProcessError:
        print(f"{tool_name} is not installed. Installing now...")
        run_command(install_command, env=env)

def check_and_install_tools():
    """Check for the presence of required tools and install them if not present."""
    gopath = get_go_path()
    os.makedirs(gopath, exist_ok=True)
    env = os.environ.copy()
    env["GOPATH"] = gopath
    env["PATH"] += os.pathsep + os.path.join(gopath, "bin")

    install_golang()

    tools_install_commands = {
        "sublist3r": (
            "git clone https://github.com/aboul3la/Sublist3r.git && "
            "cd Sublist3r && pip install -r requirements.txt && python setup.py install --user"
        ),
        "amass": "sudo apt-get install amass -y",  # amass needs sudo
        "assetfinder": "go install github.com/tomnomnom/assetfinder@latest",
        "findomain": (
            "curl -LO https://github.com/Findomain/Findomain/releases/latest/download/findomain-linux.zip && "
            "unzip -o findomain-linux.zip && chmod +x findomain && mv findomain ~/.local/bin/findomain"
        ),
        "subfinder": "sudo apt install subfinder -y",  # subfinder needs sudo
        "dnsenum": "sudo apt-get install dnsenum -y",  # dnsenum needs sudo
        "anew": "go install github.com/tomnomnom/anew@latest"
    }

    for tool, install_command in tools_install_commands.items():
        install_tool(tool, install_command, env=env)

def create_directory(path):
    """Create a directory if it does not exist, with appropriate permissions."""
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        print(f"Directory {path} created.")
    else:
        print(f"Directory already exists, appending new subdomains...\n")

def download_subdomains_list(output_folder):
    """Download the list of subdomains."""
    url = "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/DNS/subdomains-top1million-110000.txt"
    file_path = os.path.join(output_folder, "discovery-wordlist.txt")
    print(f"Downloading {url} to {file_path}")
    try:
        urllib.request.urlretrieve(url, file_path)
    except Exception as e:
        print(f"Error downloading subdomains list: {e}")

def is_valid_domain(domain):
    """Validate if the domain is in a proper format."""
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

def run_tool(tool, command, output_folder, domain):
    """Run a specific tool and process its output."""
    global total_subdomains
    print(f"Running {tool}...")
    temp_file = os.path.join(output_folder, f"{tool}_temp.txt")
    final_file = os.path.join(output_folder, f"{tool}.txt")

    # Ensure that subdomains.txt exists
    subdomains_file = os.path.join(output_folder, "subdomains.txt")
    if not os.path.exists(subdomains_file):
        open(subdomains_file, 'a').close()

    # Ensure that live_subdomains.txt exists
    live_subdomains_file = os.path.join(output_folder, "live_subdomains.txt")
    if not os.path.exists(live_subdomains_file):
        open(live_subdomains_file, 'a').close()

    try:
        # Run the command and direct output to a temporary file
        run_command(f"{command} > {temp_file}", timeout=900)

        # Ensure the final file exists before appending
        if not os.path.exists(final_file):
            open(final_file, 'a').close()

        # Extract subdomains from the temp file
        with open(temp_file, 'r') as infile, open(temp_file + "_parsed", 'w') as outfile:
            for line in infile:
                if tool == "amass":
                    # Extract subdomains for amass specific output format
                    if ' --> ' in line:
                        subdomain = line.split(' ')[0].strip()
                        if is_valid_domain(subdomain) and subdomain.endswith(domain):
                            outfile.write(subdomain + '\n')
                else:
                    subdomain = line.strip()
                    if is_valid_domain(subdomain) and subdomain.endswith(domain):
                        outfile.write(subdomain + '\n')

        # Count total subdomains found by the tool
        total_subdomains_found = len(open(temp_file + "_parsed").readlines())

        # Count existing entries in the final file before appending
        existing_entries_before = len(open(final_file).readlines())

        # Use anew to append unique entries
        run_command(f"cat {temp_file}_parsed | anew {final_file}", timeout=900)

        # Count entries in the final file after appending
        existing_entries_after = len(open(final_file).readlines())

        # Calculate the number of new entries
        new_count = existing_entries_after - existing_entries_before

        # Update total_subdomains with new subdomains
        if new_count > 0:
            with open(temp_file + "_parsed", 'r') as file:
                new_subdomains = file.read().splitlines()
            total_subdomains.update(new_subdomains)
        else:
            # Read existing subdomains if no new ones were found
            with open(final_file, 'r') as file:
                existing_subdomains = file.read().splitlines()
            total_subdomains.update(existing_subdomains)

        print(f"[+] Total Found: {len(total_subdomains)}, New to {tool}: {new_count}")

    except subprocess.CalledProcessError as e:
        print(f"Error running {tool}: {e}")
    except subprocess.TimeoutExpired as e:
        print(f"Timeout running {tool}: {e}")
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)  # Clean up temporary file
        if os.path.exists(temp_file + "_parsed"):
            os.remove(temp_file + "_parsed")  # Clean up parsed temporary file


def check_live_subdomains(subdomains_file, output_file, chunk_size=100):
    """Check which subdomains are live using httpx with a progress bar."""
    print("Checking which subdomains are live...")

    try:
        # Read subdomains from the file
        with open(subdomains_file, 'r') as file:
            subdomains = [line.strip() for line in file if is_valid_domain(line.strip())]

        total_count = len(subdomains)
        if total_count == 0:
            print("No subdomains to check.")
            return set()

        # Read existing live subdomains from the output file
        existing_live_subdomains = set()  # Added this block
        if os.path.exists(output_file):
            with open(output_file, 'r') as file:
                existing_live_subdomains = set(line.strip() for line in file)

        live_subdomains = set()
        temp_output_file = output_file + ".temp"

        # Check subdomains in chunks
        with tqdm(total=total_count, desc="Checking subdomains", unit="subdomain") as pbar:
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

        # Determine the truly new live subdomains
        new_live_subdomains = live_subdomains - existing_live_subdomains  # Added this line

        # Write the new live subdomains to the output file
        with open(output_file, 'a') as file:  # Changed to append mode
            for subdomain in new_live_subdomains:
                file.write(f"{subdomain}\n")

        print(f"{len(new_live_subdomains)} new live subdomains.")
        print(f"Live subdomains saved to {output_file}")

        # Clean up temp output file
        if os.path.exists(temp_output_file):
            os.remove(temp_output_file)

        return live_subdomains

    except subprocess.CalledProcessError as e:
        print(f"Error running httpx: {e}")
        return set()
    except subprocess.TimeoutExpired as e:
        print(f"Timeout running httpx: {e}")
        return set()





def remove_temp_files(temp_files):
    """Remove temporary files."""
    for temp_file in temp_files:
        if os.path.exists(temp_file):
            os.remove(temp_file)
        else:
            print(f"Temporary file not found, tool may have errored.")


def ensure_file_exists(file_path):
    if not os.path.isfile(file_path):
        open(file_path, 'w').close()


def main(domain):
    start_time = time.time()
    print(f"[*]  Discovery initiated for: {domain}\n")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_folder = os.path.join(base_dir, f"results/{domain}")
    create_directory(output_folder)
    
    check_and_install_tools()

    # Define the tools and their commands with temporary files
    tools = {
         "amass": f"amass enum -d {domain} -r 8.8.8.8,1.1.1.1,9.9.9.9 -norecursive -o {os.path.join(output_folder, 'amass_temp.txt')}",
        "assetfinder": f"assetfinder --subs-only {domain} > {os.path.join(output_folder, 'assetfinder_temp.txt')}",
         "sublist3r": f"sublist3r -n -d {domain} -o {os.path.join(output_folder, 'sublist3r_temp.txt')}",
         #"amass": f"amass enum -active -d {domain} -r 8.8.8.8,1.1.1.1,9.9.9.9 -o amass_run_temp.txt && grep -oP '([a-zA-Z0-9]+\.)+{domain}' {os.path.join(output_folder, 'amass_run_temp.txt')} | sort -u > {os.path.join(output_folder, 'amass_temp.txt')}",
         "findomain": f"findomain -t {domain} -u {os.path.join(output_folder, 'findomain_temp.txt')}",
         "subfinder": f"subfinder -d {domain} -o {os.path.join(output_folder, 'subfinder_temp.txt')}"
    }

    print("\n[*]  Discovering Subdomains...\n")

    # Run each tool sequentially and collect the results
    for tool, command in tools.items():
        run_tool(tool, command, output_folder, domain)

    cumulative_total_subdomains = len(total_subdomains)
    print(f"Total Subdomains Found by All Tools: {cumulative_total_subdomains}")

    # Save results to a single text file in the output directory
    all_subdomains_file = os.path.join(output_folder, "subdomains.txt")
    if total_subdomains:
        with open(all_subdomains_file, "w") as outfile:
            for subdomain in sorted(total_subdomains):
                outfile.write(subdomain + "\n")
    else:
        print(f"No new subdomains found by any tool.")

    # Check live subdomains using httpx
    live_subdomains_file = os.path.join(output_folder, "live_subdomains.txt")
    live_subdomains = check_live_subdomains(all_subdomains_file, live_subdomains_file)

        # Remove all temporary files created by the tools
    temp_files = [os.path.join(output_folder, f"{tool}_temp.txt") for tool in tools.keys()]
    for temp_file in temp_files:
        if os.path.exists(temp_file):
            os.remove(temp_file)
        if os.path.exists(f"{temp_file}_parsed"):
            os.remove(f"{temp_file}_parsed")
    
    # Remove any other temporary files with "_temp" in the name
    for file in os.listdir(output_folder):
        if "_temp" in file:
            temp_file_path = os.path.join(output_folder, file)
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                print(f"[*] Cleaning up temp files...")


    end_time = time.time()
    runtime = end_time - start_time

    # Print the results
    total_live_count = len(live_subdomains)
    print(f"Runtime: {int(runtime // 3600)}:{int((runtime % 3600) // 60)}:{int(runtime % 60)} (hh:mm:ss).")
    print(f"\n[+]  Results saved to {live_subdomains_file}.")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Subdomain enumeration script")
    parser.add_argument("domain", help="The domain to enumerate subdomains for")
    args = parser.parse_args()

    main(args.domain)
