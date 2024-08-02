#!/usr/bin/env python3

import subprocess
import os
import argparse
import urllib.request
import time
import re
import signal
from tqdm import tqdm 

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
    """Run a shell command."""
    result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True, env=env, timeout=timeout)
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
        run_command("sudo tar -C /usr/local -xzf go1.16.5.linux-amd64.tar.gz")
        os.environ["PATH"] += os.pathsep + "/usr/local/go/bin"

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
            "cd Sublist3r && pip install -r requirements.txt && sudo python setup.py install"
        ),
        "amass": "sudo apt-get install amass -y",
        "assetfinder": "go install github.com/tomnomnom/assetfinder@latest",
        "findomain": (
            "curl -LO https://github.com/Findomain/Findomain/releases/latest/download/findomain-linux.zip && "
            "unzip -o findomain-linux.zip && chmod +x findomain && sudo mv findomain /usr/bin/findomain"
        ),
        "subfinder": "sudo apt install subfinder -y",
        "dnsenum": "sudo apt-get install dnsenum -y"
    }

    for tool, install_command in tools_install_commands.items():
        install_tool(tool, install_command, env=env)

def download_subdomains_list(output_folder):
    """Download the list of subdomains."""
    url = "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/DNS/subdomains-top1million-110000.txt"
    file_path = "discovery-wordlist.txt"
    print(f"Downloading {url} to {file_path}")
    try:
        urllib.request.urlretrieve(url, file_path)
    except Exception as e:
        print(f"Error downloading subdomains list: {e}")


def check_live_subdomains(subdomains_file, output_file):
    """Check which subdomains are live using httpx with a progress bar."""
    print("Checking which subdomains are live...")
    
    # Read the subdomains from file
    with open(subdomains_file, 'r') as file:
        subdomains = [line.strip() for line in file]
    
    total_count = len(subdomains)
    live_subdomains = set()
    
    # Create a progress bar
    with tqdm(total=total_count, desc="Checking subdomains", unit="subdomain") as pbar:
        for subdomain in subdomains:
            # Run the httpx command for each subdomain (adjust as necessary)
            try:
                command = f"httpx -u {subdomain} -sc -silent -fc 404 -timeout 2 -t 300 -rl 1000 -rlm 10000"
                output = run_command(command)
                if output:
                    live_subdomains.add(subdomain)
                pbar.update(1)
            except subprocess.CalledProcessError as e:
                print(f"Error running httpx for {subdomain}: {e}")
            except subprocess.TimeoutExpired as e:
                print(f"Timeout running httpx for {subdomain}: {e}")
    
    # After all subdomains are checked
    print(f"Live subdomains saved to {output_file}")
    
    # Save results to the output file
    with open(output_file, 'w') as file:
        for subdomain in live_subdomains:
            file.write(f"{subdomain}\n")
    
    return live_subdomains


def run_tool(tool, command, output_folder, domain):
    """Run a specific tool and process its output."""
    global total_subdomains
    print(f"Running {tool}...")
    try:
        run_command(command, timeout=21100)  # Set a 30-minute timeout for each tool
        with open(os.path.join(output_folder, f"{tool}.txt"), 'r') as file:
            result = [line.strip() for line in file]
        total_subdomains.update(result)
        print(f"{tool} finished - Total Subdomains: {len(total_subdomains)}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running {tool}: {e}")
        return []
    except subprocess.TimeoutExpired as e:
        print(f"Timeout running {tool}: {e}")
        return []
        

def main(domain):
    start_time = time.time()
    print(f"Discovery initiated for: {domain}")

    output_folder = os.path.join("results", domain)
    os.makedirs(output_folder, exist_ok=True)
    
    check_and_install_tools()
    # download_subdomains_list(output_folder)

    # Define the tools and their commands
    tools = {
        "sublist3r": f"sublist3r -d {domain} -o {os.path.join(output_folder, 'sublist3r.txt')}",
        "amass": f"amass enum -d {domain} -o {os.path.join(output_folder, 'amass.txt')}",
        "assetfinder": f"assetfinder --subs-only {domain} > {os.path.join(output_folder, 'assetfinder.txt')}",
        "findomain": f"findomain -t {domain} -u {os.path.join(output_folder, 'findomain.txt')}",
        "subfinder": f"subfinder -d {domain} -o {os.path.join(output_folder, 'subfinder.txt')}"
    }

    print("Discovering Subdomains...")

    # Run each tool sequentially and collect the results
    for tool, command in tools.items():
        result = run_tool(tool, command, output_folder, domain)
        total_subdomains.update(result)

    # Save results to a single text file
    all_subdomains_file = os.path.join(output_folder, "subdomains.txt")
    with open(all_subdomains_file, "w") as outfile:
        for subdomain in sorted(total_subdomains):
            outfile.write(subdomain + "\n")
    
    # Check live subdomains using httpx
    live_subdomains_file = os.path.join(output_folder, "live_subdomains.txt")
    live_subdomains = check_live_subdomains(all_subdomains_file, live_subdomains_file)

    end_time = time.time()
    runtime = end_time - start_time

    # Print the results
    print(f"Total unique live subdomains found: {len(live_subdomains)}. Runtime: {int(runtime // 3600)}:{int((runtime % 3600) // 60)}:{int(runtime % 60)} (hh:mm:ss).")
    print(f"Subdomain enumeration complete. Results saved to {live_subdomains_file}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Subdomain enumeration script")
    parser.add_argument("domain", help="The domain to enumerate subdomains for")
    args = parser.parse_args()

    main(args.domain)
