#!/bin/bash

# Check if domain is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <domain>"
    exit 1
fi

# Define the domain and paths
DOMAIN=$1
OUTPUT_DIR="results/$DOMAIN"
SUBDOMAIN_FILE="$OUTPUT_DIR/subdomains.txt"

# Create a directory to store results
mkdir -p $OUTPUT_DIR

# Install necessary tools if not already installed
install_tools() {
    echo "Installing necessary tools..."
    go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
    go install -v github.com/OWASP/Amass/v3/...@master
    go install -v github.com/tomnomnom/assetfinder@latest
    go install -v github.com/Edu4rdSHL/findomain@latest
}

# Run Subfinder
run_subfinder() {
    echo "Running Subfinder..."
    subfinder -d $DOMAIN -o $OUTPUT_DIR/subfinder.txt -silent
}

# Run Amass
run_amass() {
    echo "Running Amass..."
    amass enum -passive -d $DOMAIN -o $OUTPUT_DIR/amass.txt
}

# Run Assetfinder
run_assetfinder() {
    echo "Running Assetfinder..."
    assetfinder --subs-only $DOMAIN > $OUTPUT_DIR/assetfinder.txt
}

# Run Findomain
run_findomain() {
    echo "Running Findomain..."
    findomain -t $DOMAIN -u $OUTPUT_DIR/findomain.txt
}

# Combine results
combine_results() {
    echo "Combining results..."
    cat $OUTPUT_DIR/subfinder.txt $OUTPUT_DIR/amass.txt $OUTPUT_DIR/assetfinder.txt $OUTPUT_DIR/findomain.txt | sort -u > $SUBDOMAIN_FILE
}

# Function to run all steps
run_all() {
    install_tools
    run_subfinder
    run_amass
    run_assetfinder
    run_findomain
    combine_results
}

# Run the script
run_all

# Output results
echo "Subdomain discovery complete. Results saved in $SUBDOMAIN_FILE"
