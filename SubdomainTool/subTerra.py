#!/usr/bin/env python3

import concurrent.futures
import subprocess
import os
import argparse
import urllib.request
import time
import re
from tqdm import tqdm
import shutil
import idna

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
        print(f"Directory already exists, appending new subdomains...")

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
    global total_subdomains
    print(f"Running {tool}...")
    temp_file = os.path.join(output_folder, f"{tool}_temp.txt")
    temp_file_run = os.path.join(output_folder, f"{tool}_run_temp.txt")
    valid_temp_file = f"{temp_file}_valid"
    final_file = os.path.join(output_folder, f"{tool}.txt")

    # Define file paths
    temp_file = os.path.join(output_folder, f"{tool}_temp.txt")
    temp_file_run = os.path.join(output_folder, f"{tool}_run_temp.txt")
    valid_temp_file = f"{temp_file}_valid"
    final_file = os.path.join(output_folder, f"{tool}.txt")

    all_subdomains_file = os.path.join(output_folder, "subdomains.txt")
    live_subdomains_file = os.path.join(output_folder, "live_subdomains.txt")

    # Ensure that the required files exist
    ensure_file_exists(temp_file)
    ensure_file_exists(temp_file_run)
    ensure_file_exists(valid_temp_file)
    ensure_file_exists(final_file)
    ensure_file_exists(all_subdomains_file)
    ensure_file_exists(live_subdomains_file)
    

    try:
        # Run the command and direct output to a temporary file
        run_command(f"{command} > {temp_file}", timeout=900)

        # Filter valid subdomains from the temp file
        with open(temp_file, 'r') as infile, open(valid_temp_file, 'w') as outfile:
            for line in infile:
                subdomain = line.strip()
                if is_valid_domain(subdomain):
                    outfile.write(subdomain + '\n')

        # Ensure the final file exists before appending
        if not os.path.exists(final_file):
            open(final_file, 'a').close()

        # Count existing entries in the final file before appending
        existing_entries_before = len(open(final_file).readlines())

        # Append unique subdomains to the final file using anew and count new entries
        result = run_command(f"cat {valid_temp_file} | anew {final_file}", timeout=900)
        new_subdomains = result.splitlines()
        new_count = len(new_subdomains)

        # Read valid subdomains from the valid_temp_file
        with open(valid_temp_file, 'r') as file:
            new_subdomains = set(file.read().splitlines())

        # Update total_subdomains with new subdomains
        total_subdomains.update(new_subdomains)

        print(f"{tool} finished - Total Subdomains Found: {len(new_subdomains)}, New: {new_count}")
    except subprocess.CalledProcessError as e:
        print(f"Error running {tool}: {e}")
    except subprocess.TimeoutExpired as e:
        print(f"Timeout running {tool}: {e}")
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)
        if os.path.exists(valid_temp_file):
            os.remove(valid_temp_file)
        if os.path.exists(temp_file_run):
            os.remove(temp_file_run)


def run_httpx(subdomain):
    """Function to run httpx for a single subdomain"""
    command = f"echo {subdomain} | httpx -silent -mc 200"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return subdomain if result.returncode == 0 and result.stdout.strip() else None

def check_live_subdomains(subdomains_file, output_file, max_workers=10):
    print("Checking which subdomains are live...")

    temp_live_file = f"{output_file}.temp"

    # Read the subdomains from the file
    with open(subdomains_file, 'r') as file:
        subdomains = [line.strip() for line in file if is_valid_domain(line.strip())]

    total_count = len(subdomains)
    live_subdomains = set()

    if total_count == 0:
        print("No subdomains to check.")
        return live_subdomains

    with tqdm(total=total_count, desc="Checking subdomains", unit="subdomain") as pbar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_subdomain = {executor.submit(run_httpx, subdomain): subdomain for subdomain in subdomains}
            for future in concurrent.futures.as_completed(future_to_subdomain):
                subdomain = future_to_subdomain[future]
                try:
                    result = future.result()
                    if result:
                        live_subdomains.add(result)
                except Exception as exc:
                    print(f"{subdomain} generated an exception: {exc}")
                finally:
                    pbar.update(1)

    live_count = len(live_subdomains)
    print(f"Live Subdomains Found: {live_count}")

    if live_subdomains:
        with open(temp_live_file, 'w') as file:
            for subdomain in live_subdomains:
                file.write(f"{subdomain}\n")

        # Append unique live subdomains to the final file using anew and suppress the output
        subprocess.run(f"cat {temp_live_file} | anew {output_file} > /dev/null 2>&1", shell=True)

        if os.path.exists(temp_live_file):
            os.remove(temp_live_file)

    return live_subdomains


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
    print(f"Discovery initiated for: {domain}\n")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_folder = os.path.join(base_dir, f"results/{domain}")
    create_directory(output_folder)
    
    check_and_install_tools()

    # Define the tools and their commands with temporary files
    tools = {
        # "amass": f"amass enum -d {domain} -r 8.8.8.8,1.1.1.1,9.9.9.9 -norecursive -o {os.path.join(output_folder, 'amass_temp.txt')}",
        "assetfinder": f"assetfinder --subs-only {domain} > {os.path.join(output_folder, 'assetfinder_temp.txt')}",
        # "sublist3r": f"sublist3r -n -d {domain} -o {os.path.join(output_folder, 'sublist3r_temp.txt')}",
        # "amass": f"amass enum -d {domain} -r 8.8.8.8,1.1.1.1,9.9.9.9 -o amass_run_temp.txt && grep -oP '([a-zA-Z0-9]+\.)+{domain}' {os.path.join(output_folder, 'amass_run_temp.txt')} | sort -u > {os.path.join(output_folder, 'amass_temp.txt')}",
         #"findomain": f"findomain -t {domain} -u {os.path.join(output_folder, 'findomain_temp.txt')}",
         #"subfinder": f"subfinder -d {domain} -o {os.path.join(output_folder, 'subfinder_temp.txt')}"
    }

    print("Discovering Subdomains...")

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

    end_time = time.time()
    runtime = end_time - start_time

    # Print the results
    total_live_count = len(live_subdomains)
    print(f"Total unique live subdomains found: {total_live_count}.\nRuntime: {int(runtime // 3600)}:{int((runtime % 3600) // 60)}:{int(runtime % 60)} (hh:mm:ss).")
    print(f"Subdomain enumeration complete. Results saved to {live_subdomains_file}.")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Subdomain enumeration script")
    parser.add_argument("domain", help="The domain to enumerate subdomains for")
    args = parser.parse_args()

    main(args.domain)
