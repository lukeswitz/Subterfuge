# Subterfuge Subdomain Finder

Discover hidden subdomains using multiple advanced tools and compile them into a single file for use with Subterfuge.

## Tools Used
- **Subfinder**: Fast passive subdomain enumeration.
- **Amass**: In-depth DNS enumeration and subdomain discovery.
- **Assetfinder**: Quickly finds subdomains and IP addresses.
- **Findomain**: Efficient subdomain enumeration tool.

## Prerequisites

Ensure the following tools are installed on your system:
- **Golang**: Required for installing Go-based tools.

## Installation

Run the script to install the necessary tools:

```bash
chmod +x subterfuge_finder.sh
./subterfuge_finder.sh
```

## Usage

Run the Script with a Domain:

```bash
./subterfuge_finder.sh example.com
Replace example.com with your target domain.
```

## Output

- The script will save the discovered subdomains in the results/$DOMAIN/subdomains.txt file.

## Contributing

Feel free to contribute by opening issues or submitting pull requests to improve this script.

## License

This project is licensed under the MIT License.
