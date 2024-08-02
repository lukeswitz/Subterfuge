# Subterfuge Subdomain Finder

Discover hidden subdomains using multiple advanced tools and compile them into a single file. Each is checked to be alive using httpx. A final list is stored in a folder for use with Subterfuge.

## Tools Used

- **Amass**
- **Assetfinder**
- **DNSEnum** 
- **Findomain**
- **Subfinder**
- **Sublist3r**
- **httpx**

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
### Disable httpx check
Comment out the line around `170` as shown:

` # live_subdomains = check_live_subdomains(all_subdomains_file, live_subdomains_file)`

## Sample Output
(with amass disabled)
```
Discovery initiated for: tesla.com
sublist3r is already installed.
amass is already installed.
assetfinder is already installed.
findomain is already installed.
subfinder is already installed.
dnsenum is already installed.
Discovering Subdomains...
Running sublist3r...
sublist3r finished - Total Subdomains: 326
Running assetfinder...
assetfinder finished - Total Subdomains: 380
Running findomain...
findomain finished - Total Subdomains: 713
Running subfinder...
subfinder finished - Total Subdomains: 1219
Checking which subdomains are live...
Checking subdomains:  19%|███████▊                                | 237/1219 [04:56<15:40,  1.04subdomain/s]
```

- The script will save the discovered subdomains in the results/$DOMAIN/subdomains.txt file to be used with Subterfuge.

## Contributing

Feel free to contribute by opening issues or submitting pull requests to improve this script.

## License

This project is licensed under the MIT License.
