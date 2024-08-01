import subprocess
import os
import argparse
import urllib.request
import time

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
    """Install a specific tool."""
    try:
        run_command(f"which {tool_name}", env=env)
    except subprocess.CalledProcessError:
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
            "cd Sublist3r && sudo pip install -r requirements.txt && sudo python setup.py install"
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
    url = "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/DNS/combined_subdomains.txt"
    file_path = os.path.join(output_folder, "subdomains-top-1million.txt")
    print(f"Downloading {url} to {file_path}")
    try:
        urllib.request.urlretrieve(url, file_path)
    except Exception as e:
        print(f"Error downloading subdomains list: {e}")

def create_resolvers_file(output_folder):
    """Create a resolvers file."""
    resolvers = [
        "8.8.8.8",
        "8.8.4.4",
        "1.1.1.1",
        "1.0.0.1",
        "9.9.9.9",
        "208.67.222.222",
        "208.67.220.220"
    ]

    file_path = os.path.join(output_folder, "resolvers.txt")
    with open(file_path, "w") as file:
        for resolver in resolvers:
            file.write(resolver + "\n")

def run_tool(tool, command, output_folder):
    """Run a specific tool and process its output."""
    print(f"Running {tool}...")
    try:
        run_command(command, timeout=1800)  # Set a 30-minute timeout for each tool
        if tool == "dnsenum":
            result = parse_dnsenum_output(os.path.join(output_folder, 'dnsenum.txt'))
        else:
            with open(os.path.join(output_folder, f"{tool}.txt"), 'r') as file:
                result = [line.strip() for line in file]
        total_subdomains.update(result)
        print(f"{tool} finished - Subdomains found: {len(result)}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running {tool}: {e}")
        return []
    except subprocess.TimeoutExpired as e:
        print(f"Timeout running {tool}: {e}")
        return []

def parse_dnsenum_output(filename):
    """Parse the dnsenum output file to extract brute-forced subdomains."""
    subdomains = set()
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
            in_brute_force_section = False
            for line in lines:
                if "Brute forcing with" in line:
                    in_brute_force_section = True
                    continue
                if in_brute_force_section:
                    if line.strip() and not line.startswith("___"):  # Skip headers and empty lines
                        subdomain = line.strip()
                        subdomains.add(subdomain)
    except FileNotFoundError:
        print(f"File {filename} not found.")
    return subdomains

def main(domain):
    start_time = time.time()
    print(f"Discovery initiated for: {domain}")

    output_folder = os.path.join("results", domain)
    os.makedirs(output_folder, exist_ok=True)
    
    check_and_install_tools()
    download_subdomains_list(output_folder)
    create_resolvers_file(output_folder)

    # Define the tools and their commands
    tools = {
        "sublist3r": f"sublist3r -d {domain} -o {os.path.join(output_folder, 'sublist3r.txt')}",
        "amass": f"amass enum -d {domain} -o {os.path.join(output_folder, 'amass.txt')}",
        "assetfinder": f"assetfinder --subs-only {domain} > {os.path.join(output_folder, 'assetfinder.txt')}",
        "findomain": f"findomain -t {domain} -u {os.path.join(output_folder, 'findomain.txt')}",
        "subfinder": f"subfinder -d {domain} -o {os.path.join(output_folder, 'subfinder.txt')}",
        "dnsenum": f"dnsenum {domain} -f {os.path.join(output_folder, 'subdomains-top-1million.txt')} --subfile {os.path.join(output_folder, 'dnsenum.txt')}"
    }

    print("Discovering Subdomains...")

    # Run each tool sequentially and collect the results
    for tool, command in tools.items():
        result = run_tool(tool, command, output_folder)
        total_subdomains.update(result)

    # Save results to a single text file
    with open(os.path.join(output_folder, "subdomains.txt"), "w") as outfile:
        for subdomain in sorted(total_subdomains):
            outfile.write(subdomain + "\n")

    end_time = time.time()
    runtime = end_time - start_time

    print(f"Total unique subdomains found: {len(total_subdomains)}. Runtime: {int(runtime // 3600)}:{int((runtime % 3600) // 60)}:{int(runtime % 60)} (hh:mm:ss).")
    print(f"Subdomain enumeration complete. Results saved to {os.path.join(output_folder, 'subdomains.txt')}.")

    # Clean up temporary files
    os.remove(os.path.join(output_folder, "subdomains-top-1million.txt"))
    os.remove(os.path.join(output_folder, "resolvers.txt"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Subdomain enumeration script")
    parser.add_argument("domain", help="The domain to enumerate subdomains for")
    args = parser.parse_args()

    main(args.domain)
