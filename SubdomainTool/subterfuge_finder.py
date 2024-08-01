import subprocess
import os
import argparse
import urllib.request
import time
import concurrent.futures
from threading import Lock

# Initialize a lock for thread-safe operations
lock = Lock()
total_subdomains = set()

def run_command(command, env=None):
    """Run a shell command."""
    result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True, env=env)
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

def download_subdomains_list():
    url = "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/DNS/combined_subdomains.txt"
    file_name = "subdomains-top-1million.txt"
    print(f"Downloading {url} to {file_name}")
    try:
        urllib.request.urlretrieve(url, file_name)
    except Exception as e:
        print(f"Error downloading subdomains list: {e}")

def create_resolvers_file():
    resolvers = [
        "8.8.8.8",
        "8.8.4.4",
        "1.1.1.1",
        "1.0.0.1",
        "9.9.9.9",
        "208.67.222.222",
        "208.67.220.220"
    ]

    with open("resolvers.txt", "w") as file:
        for resolver in resolvers:
            file.write(resolver + "\n")

def run_tool(tool, command):
    try:
        run_command(command)
        with open(f"{tool}.txt", 'r') as file:
            result = [line.strip() for line in file]
        with lock:
            total_subdomains.update(result)
            print(f"{tool} finished - Subdomains found: {len(total_subdomains)}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running {tool}: {e}")
        return []

def main(domain):
    start_time = time.time()
    print(f"Discovery initiated for: {domain}")
    
    check_and_install_tools()
    download_subdomains_list()
    create_resolvers_file()

    # Define the tools and their commands
    tools = {
        "sublist3r": f"sublist3r -d {domain} -o sublist3r.txt",
        "amass": f"amass enum -d {domain} -o amass.txt",
        "assetfinder": f"assetfinder --subs-only {domain} > assetfinder.txt",
        "findomain": f"findomain -t {domain} -u findomain.txt",
        "subfinder": f"subfinder -d {domain} -o subfinder.txt",
        "dnsenum": f"dnsenum {domain} --enum -f subdomains-top-1million.txt --dnsserver 8.8.8.8 --dnsserver 8.8.4.4 --dnsserver 1.1.1.1 --dnsserver 1.0.0.1 --dnsserver 9.9.9.9 --dnsserver 208.67.222.222 --dnsserver 208.67.220.220 --subfile dnsenum.txt"
    }

    print("Discovering subdomains.")

    # Run each tool in parallel and collect the results
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(run_tool, tool, command): tool for tool, command in tools.items()}
        for future in concurrent.futures.as_completed(futures):
            future.result()

    # Save results to a single text file
    with open("subdomains.txt", "w") as outfile:
        for subdomain in sorted(total_subdomains):
            outfile.write(subdomain + "\n")

    end_time = time.time()
    runtime = end_time - start_time

    print(f"Total unique subdomains found: {len(total_subdomains)}. Runtime: {int(runtime // 3600)}:{int((runtime % 3600) // 60)}:{int(runtime % 60)} (hh:mm:ss).")
    print("Subdomain enumeration complete. Results saved to subdomains.txt.")
    
    # Clean up temporary files
    os.remove("subdomains-top-1million.txt")
    os.remove("resolvers.txt")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Subdomain enumeration script")
    parser.add_argument("domain", help="The domain to enumerate subdomains for")
    args = parser.parse_args()

    main(args.domain)
