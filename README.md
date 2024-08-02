# Subterfuge
A comprehensive tool for subdomain discovery and permutation generation.

> [!IMPORTANT]  
> Subdomain discovery is needed in a subdomains.txt file if you don't use the included subdomain finder tool. 
```
├── README.md
├── SubdomainTool
│   ├── results
│   │   └── tesla.com
│   │       ├── subdomains.txt
│   └── subTerra.py
├── subterfuge.py
```

## Workflow

1. **Subdomain Discovery**:
    - `subTerra.py` discovers subdomains using a deep set of tooling.
    - Discovered subdomains are saved in a text file in their respective folders.

2. **Permutation Generation and Validation**:
    - `subterfuge.py` generates patterns and uses them with permutation tools listed below. They are checked with httpx to ensure live domains are saved as the final output.

## Installation

Both scripts will automatically install necessary tools if not already installed:

## Tools

### Discovery
- **subfinder**
- **sublist3r**
- **amass**: 
- **assetfinder**
- **findomain**
- **dnsenum**

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
chmod +x subTerra.py
python3 subTerra.py example.com
```

> [!WARNING]  
> Generated lists of permutations can be large, into the GB's.
> You can tone this down by simply removing some flags from the script commands.

### Step 2: Generate Permutations and Check Validity

Navigate back to the root directory and run:
```bash
cd ..
chmod +x subterfuge.py
./subterfuge.py example.com
```

Example Output:
```
Discovery initiated for: tesla.com
Generating patterns from discovered subdomains...
Patterns generated and saved to /home/dev/Subterfuge/results/tesla.com/patterns.txt
Number of subdomains: 2770
Number of patterns: 612
Running alterx...
alterx finished - Permutations found: 612
Running gotator...
```


## Contributing

Open issues or submit pull requests to contribute.

## License

Licensed under the MIT License.
