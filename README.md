# Subterfuge

A comprehensive tool for subdomain discovery and permutation generation.

## Workflow

1. **Subdomain Discovery**:
    - `subterfuge_finder.sh` discovers subdomains using advanced tools.
    - Discovered subdomains are saved in a text file.

2. **Permutation Generation and Validation**:
    - `subterfuge.sh` generates permutations and checks if they are live.
  
## Installation

Both scripts will automatically install necessary tools if not already installed:

## Tools

### Discovery
- **Subfinder**: Fast subdomain enumeration.
- **Amass**: In-depth DNS enumeration.
- **Assetfinder**: Quick subdomain discovery.
- **Findomain**: Efficient subdomain enumeration.

### Permutation and Validation
- **AlterX**: Subdomain permutation generator.
- **Gotator**: Generates permutations and combinations.
- **AltDNS**: Generates permutations, alterations, and mutations.
- **DnsGen**: Generates permutations from a wordlist.
- **Ripgen**: Generates permutations from subdomains.
- **Lepus**: Uses a Markov chain model for permutations.
- **PureDNS**: Resolves subdomains.
- **Httpx**: Checks live subdomains.

## Usage

### Step 1: Discover Subdomains

Navigate to the `SubdomainTool` directory and run:
```bash
cd SubdomainTool
chmod +x subterfuge_finder.sh
./subterfuge_finder.sh example.com
```

### Step 2: Generate Permutations and Check Validity

Navigate back to the root directory and run:
```bash
cd ..
chmod +x subterfuge.sh
./subterfuge.sh example.com
```


## Contributing

Open issues or submit pull requests to contribute.

## License

Licensed under the MIT License.
