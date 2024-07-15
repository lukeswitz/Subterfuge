# Subterfuge

Subterfuge is a comprehensive subdomain tool designed to uncover hidden subdomains with generated permutations.

## Contents

1. **subterfuge.sh**: Generate permutations based on discovered subdomains.
2. **SubdomainTool/**: Contains a subdomain discovery script to populate subdomains.txt if you don't happen to have a list available. 

README.

## Usage

1. **Discover Subdomains**:
   - Navigate to the `SubdomainTool` directory.
   - Run the `subterfuge_finder.sh` script with the target domain:
     ```bash
     cd SubdomainTool
     chmod +x subterfuge_finder.sh
     ./subterfuge_finder.sh example.com
     ```
   - This will save the discovered subdomains in `SubdomainTool/results/example.com/subdomains.txt`.

2. **Generate Permutations**:
   - Navigate back to the root directory.
   - Run the `subterfuge.sh` script:
     ```bash
     cd ..
     chmod +x subterfuge.sh
     ./subterfuge.sh example.com
     ```
   - This will use the `SubdomainTool/results/example.com/subdomains.txt` file to generate permutations and resolve them.

## Installation

Both scripts will automatically install the necessary tools if they are not already installed.

## Contributing

Feel free to contribute by opening issues or submitting pull requests to improve this tool.

## License

This project is licensed under the MIT License.
