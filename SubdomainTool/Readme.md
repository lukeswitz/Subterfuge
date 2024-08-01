# Subterfuge Subdomain Finder

Discover hidden subdomains using multiple advanced tools and compile them into a single file. Stored for use with Subterfuge.

## Tools Used

- **Amass**
- **Assetfinder**
- **DNSEnum** 
- **Findomain**
- **Subfinder**
- **Sublist3r**

## Prerequisites

Ensure the following tools are installed on your system:
- **Golang**: Required for installing Go-based tools.

## Installation

Run the script to install the necessary tools

## Usage

Run the Script with a Domain:

```bash
python3 subterfuge_finder.py example.com
```

## Output

- The script will save the discovered subdomains in the results/$DOMAIN/subdomains.txt file to be used with Subterfuge.

## Contributing

Feel free to contribute by opening issues or submitting pull requests to improve this script.

## License

This project is licensed under the MIT License.
