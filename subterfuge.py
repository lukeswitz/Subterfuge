import os
import subprocess
import sys
import time
import argparse

total_subdomains = set()

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
    """Check if the domain is valid."""
    if not domain:
        return False
    parts = domain.split('.')
    if len(parts) < 2:
        return False
    if not all(part.isalnum() or part == '-' for part in parts):
        return False
    return True

def generate_patterns(subdomain_file, patterns_file, domain):
    print("Generating patterns from discovered subdomains...")
    valid_patterns = set()
    common_words = ['admin', 'test', 'dev', 'prod', 'stage', 'qa', 'demo', 'beta', 'internal']
    with open(subdomain_file, 'r') as sf:
        for subdomain in sf:
            subdomain = subdomain.strip()
            if is_valid_domain(subdomain):
                parts = subdomain.split('.')
                if len(parts) > 1:
                    prefix = parts[0]
                    suffix = domain
                    valid_patterns.add(f"{prefix}.{suffix}")
                    valid_patterns.add(f"{prefix}-{suffix}")
                    valid_patterns.add(f"{prefix}{suffix}")
                    for word in common_words:
                        valid_patterns.add(f"{word}.{suffix}")
                        valid_patterns.add(f"{prefix}-{word}.{suffix}")
                        valid_patterns.add(f"{word}-{prefix}.{suffix}")

    predefined_patterns = [
        f"{{{{number}}}}-{{{{sub}}}}.{domain}",
        f"{{{{number}}}}{{{{word}}}}.{domain}",
        f"{{{{region}}}}-{{{{sub}}}}-{{{{word}}}}.{domain}",
        f"{{{{region}}}}-{{{{sub}}}}.{domain}",
        f"{{{{region}}}}.{{{{sub}}}}.{domain}",
        f"{{{{sub}}}}-{{{{number}}}}-{{{{word}}}}.{domain}",
        f"{{{{sub}}}}-{{{{number}}}}.{domain}",
        f"{{{{sub}}}}-{{{{region}}}}.{domain}",
        f"{{{{sub}}}}-{{{{word}}}}-{{{{number}}}}.{domain}",
        f"{{{{sub}}}}-{{{{word}}}}-{{{{region}}}}.{domain}",
        f"{{{{sub}}}}-{{{{word}}}}.{domain}",
        f"{{{{sub}}}}.{{{{word}}}}.{domain}",
        f"{{{{sub}}}}{{{{number}}}}.{domain}",
        f"{{{{sub}}}}{{{{word}}}}.{domain}",
        f"{{{{word}}}}-{{{{number}}}}.{domain}",
        f"{{{{word}}}}-{{{{sub}}}}-{{{{number}}}}.{domain}",
        f"{{{{word}}}}-{{{{sub}}}}.{domain}",
        f"{{{{word}}}}.{{{{sub}}}}-{{{{number}}}}.{domain}",
        f"{{{{word}}}}.{{{{sub}}}}.{domain}",
        f"{{{{word}}}}{{{{number}}}}.{domain}"
    ]

    valid_patterns.update(predefined_patterns)

    # Patterns to exclude
    patterns_to_exclude = {
        f"{{{{number}}}}{{{{word}}}}.{domain}",
        f"{{{{region}}}}.{{{{sub}}}}.{domain}",
        f"{{{{sub}}}}.{{{{word}}}}.{domain}",
        f"{{{{sub}}}}{{{{number}}}}.{domain}",
        f"{{{{sub}}}}{{{{word}}}}.{domain}",
        f"{{{{word}}}}.{{{{sub}}}}.{domain}",
        f"{{{{word}}}}{{{{number}}}}.{domain}"
    }

    valid_patterns = {pattern for pattern in valid_patterns if is_valid_domain(pattern.replace("{{sub}}", "example").replace("{{word}}", "example").replace("{{number}}", "123").replace("{{region}}", "us")) and pattern not in patterns_to_exclude}

    with open(patterns_file, 'w') as pf:
        for pattern in sorted(valid_patterns):
            pf.write(f"{pattern}\n")
    print(f"Patterns generated and saved to {patterns_file}")

def run_tool(tool, command):
    global total_subdomains
    print(f"Running {tool}...")
    try:
        run_command(command, timeout=1800)  # Set a 30-minute timeout for each tool
        permutations_file = command.split()[-1]
        with open(permutations_file, 'r') as file:
            result = [line.strip() for line in file]
        total_subdomains.update(result)
        print(f"{tool} finished - Permutations found: {len(total_subdomains)}")
    except subprocess.CalledProcessError as e:
        print(f"Error running {tool}: {e}")
    except subprocess.TimeoutExpired as e:
        print(f"Timeout running {tool}: {e}")

def check_live_subdomains(subdomains_file, output_file):
    """Check which subdomains are live using httpx."""
    print("Checking which subdomains are live...")
    try:
        run_command(f"httpx -l {subdomains_file} -o {output_file} --silent")
        print(f"Live subdomains saved to {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error running httpx: {e}")

def count_lines(file_path):
    return int(subprocess.check_output(['wc', '-l', file_path]).split()[0])
    
def main(domain):
    start_time = time.time()
    print(f"Discovery initiated for: {domain}")

    output_folder = os.path.abspath(f"results/{domain}")
    os.makedirs(output_folder, exist_ok=True)
    subdomain_file = os.path.abspath(f"SubdomainTool/results/{domain}/subdomains.txt")
    patterns_file = os.path.abspath(f"{output_folder}/patterns.txt")

    check_and_install_tools()

    if not os.path.exists(subdomain_file):
        print(f"No subdomain file found at {subdomain_file}")
        return

    generate_patterns(subdomain_file, patterns_file, domain)
    
    subdomain_count = count_lines(subdomain_file)
    pattern_count = count_lines(patterns_file)
    print(f"Number of subdomains: {subdomain_count}")
    print(f"Number of patterns: {pattern_count}")

    tools = {
                "alterx": f"alterx -l {subdomain_file} -p {patterns_file} -o {output_folder}/alterx_permutations.txt",
        "gotator": f"gotator -sub {subdomain_file} -perm {patterns_file} -depth 1 -numbers 5 -mindup -adv -md > {output_folder}/gotator_permutations.txt",
        "altdns": f"altdns -i {subdomain_file} -o {output_folder}/altdns_permutations.txt -w {patterns_file}",
        "dnsgen": f"dnsgen -f {subdomain_file} -w {patterns_file} > {output_folder}/dnsgen_permutations.txt",
        "ripgen": f"ripgen {subdomain_file} {patterns_file} > {output_folder}/ripgen_permutations.txt",
        "lepus": f"lepus.py --permutate -pw {patterns_file} -o {output_folder}/lepus_permutations.txt {subdomain_file}"
    }

    for tool, command in tools.items():
        run_tool(tool, command)

    # Combine all permutations into one file
    all_permutations_file = os.path.abspath(f"{output_folder}/all_permutations.txt")
    with open(all_permutations_file, 'w') as outfile:
        for tool, _ in tools.items():
            permutations_file = os.path.join(output_folder, f"{tool}_permutations.txt")
            if os.path.exists(permutations_file):
                with open(permutations_file, 'r') as infile:
                    for line in infile:
                        outfile.write(line)

    # Check live subdomains using httpx
    live_subdomains_file = os.path.abspath(f"{output_folder}/live_subdomains.txt")
    check_live_subdomains(all_permutations_file, live_subdomains_file)

    end_time = time.time()
    runtime = end_time - start_time

    print(f"Total unique live subdomains found: {len(total_subdomains)}. Runtime: {int(runtime // 3600)}:{int((runtime % 3600) // 60)}:{int(runtime % 60)} (hh:mm:ss).")
    print(f"Subdomain enumeration complete. Results saved to {output_folder}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Subdomain enumeration script")
    parser.add_argument("domain", help="The domain to enumerate subdomains for")
    args = parser.parse_args()

    main(args.domain)
