#!/bin/bash

# Check if domain is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <domain>"
    exit 1
fi

# Define the domain and paths
DOMAIN=$1
SUBDOMAIN_FILE="SubdomainTool/results/$DOMAIN/subdomains.txt"
OUTPUT_DIR="results/$DOMAIN"

# Create a directory to store results
mkdir -p $OUTPUT_DIR

# Install necessary tools if not already installed
install_tools() {
    echo "Installing necessary tools..."
    go install -v github.com/projectdiscovery/alterx/cmd/alterx@latest
    go install -v github.com/Josue87/gotator@latest
    pip install altdns
    go install -v github.com/d3mondev/puredns@latest
    pip install ripgen
    pip install lepus
    go install -v github.com/ProjectAnte/dnsgen@latest
}

# Function to generate patterns based on discovered subdomains
generate_patterns() {
    echo "Generating patterns from discovered subdomains..."
    echo "patterns:" > patterns.yaml
    
    # Extract prefixes and suffixes from the subdomains
    while read -r subdomain; do
        prefix=$(echo "$subdomain" | awk -F'.' '{print $1}')
        suffix=$(echo "$subdomain" | awk -F'.' '{print $(NF-1)}')
        echo "  - \"${prefix}.${suffix}\"" >> patterns.yaml
        echo "  - \"${prefix}-${suffix}\"" >> patterns.yaml
        echo "  - \"${prefix}${suffix}\"" >> patterns.yaml
    done < $SUBDOMAIN_FILE

    # Add some predefined patterns
    cat <<EOL >> patterns.yaml
  - "{{sub}}-{{word}}.{{suffix}}"
  - "{{word}}-{{sub}}.{{suffix}}"
  - "{{sub}}.{{word}}.{{suffix}}"
  - "{{word}}.{{sub}}.{{suffix}}"
  - "{{sub}}{{number}}.{{suffix}}"
  - "{{sub}}{{word}}.{{suffix}}"
  - "{{region}}.{{sub}}.{{suffix}}"
  - "{{sub}}-{{number}}.{{suffix}}"
  - "{{number}}-{{sub}}.{{suffix}}"
  - "{{word}}-{{number}}.{{suffix}}"
  - "{{sub}}-{{number}}.{{word}}.{{suffix}}"
  - "{{word}}-{{sub}}-{{number}}.{{suffix}}"
  - "{{sub}}-{{region}}.{{suffix}}"
  - "{{region}}-{{sub}}.{{suffix}}"
  - "{{word}}{{number}}.{{suffix}}"
  - "{{number}}{{word}}.{{suffix}}"
  - "{{sub}}-{{word}}-{{number}}.{{suffix}}"
  - "{{sub}}-{{word}}-{{region}}.{{suffix}}"
  - "{{region}}-{{sub}}-{{word}}.{{suffix}}"
  - "{{word}}.{{sub}}-{{number}}.{{suffix}}"
  - "{{sub}}-{{number}}.{{suffix}}"
EOL
}

# Function to run AlterX
run_alterx() {
    echo "Running AlterX for $DOMAIN"
    alterx -l $SUBDOMAIN_FILE -p patterns.yaml -o $OUTPUT_DIR/alterx_permutations.txt
}

# Function to run Gotator
run_gotator() {
    echo "Running Gotator for $DOMAIN"
    gotator -sub $SUBDOMAIN_FILE -perm $PERMUTATION_WORDLIST -depth 2 -numbers 10 -mindup -adv -md > $OUTPUT_DIR/gotator_permutations.txt
}

# Function to run AltDNS
run_altdns() {
    echo "Running AltDNS for $DOMAIN"
    altdns -i $SUBDOMAIN_FILE -o $OUTPUT_DIR/altdns_permutations.txt -w $PERMUTATION_WORDLIST
}

# Function to run DnsGen
run_dnsgen() {
    echo "Running DnsGen for $DOMAIN"
    dnsgen $SUBDOMAIN_FILE -w $PERMUTATION_WORDLIST -o $OUTPUT_DIR/dnsgen_permutations.txt
}

# Function to run Ripgen
run_ripgen() {
    echo "Running Ripgen for $DOMAIN"
    ripgen -i $SUBDOMAIN_FILE -w $PERMUTATION_WORDLIST -o $OUTPUT_DIR/ripgen_permutations.txt
}

# Function to run Lepus
run_lepus() {
    echo "Running Lepus for $DOMAIN"
    lepus.py --permutate -pw $PERMUTATION_WORDLIST -o $OUTPUT_DIR/lepus_permutations.txt $SUBDOMAIN_FILE
}

# Function to resolve permutations
resolve_permutations() {
    echo "Resolving permutations"
    cat $OUTPUT_DIR/*_permutations.txt | sort -u > $OUTPUT_DIR/all_permutations.txt
    puredns resolve $OUTPUT_DIR/all_permutations.txt -o $OUTPUT_DIR/live_subdomains.txt
}

# Function to run all steps
run_all() {
    install_tools
    generate_patterns
    run_alterx
    run_gotator
    run_altdns
    run_dnsgen
    run_ripgen
    run_lepus
    resolve_permutations
}

# Run the script
run_all

# Output results
echo "Total unique permutations found: $(wc -l < $OUTPUT_DIR/all_permutations.txt)"
echo "Total live subdomains found: $(wc -l < $OUTPUT_DIR/live_subdomains.txt)"
