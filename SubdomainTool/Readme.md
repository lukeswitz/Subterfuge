# SubTerra 
Powerful Subdomain Enumeration:

- Each valid subdomain is checked for life using httpx.
- A final list is stored in a folder for use with Subterfuge.

## Prerequisites

- **Golang**: Subterra will install this and all other necessary tools if they are not found on the system. 

## Usage

Run the Script with a Domain:

```bash
python3 subterfuge_finder.py example.com
```

> [!NOTE]  
> Turn off live domain check or enable amass:

#### 1. Disable httpx check
Comment out the line around `170` as shown:

` # live_subdomains = check_live_subdomains(all_subdomains_file, live_subdomains_file)`


#### 2. Enable amass:
Remove the `#` around line 180 for the amss command to enable it. Amass takes a lot of time and API use if configured.

`   # "amass": f"amass....`

## Sample Output
Shown with amass disabled, as it is by default. 
```
           _                                 
           | |     _                          
  ___ _   _| |__ _| |_ _____  ____ ____ _____ 
 /___) | | |  _ (_   _) ___ |/ ___) ___|____ |
|___ | |_| | |_) )| |_| ____| |  | |   / ___ |
(___/|____/|____/  \__)_____)_|  |_|   \_____|

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

- The script will create a folder for the target.
- Discovered subdomains will be saved in the results/example.com/ folder to be used with Subterfuge, etc.
- The resulting `subdomains.txt` combined output will be checked for live status codes using httpx and saved to `live_subdomains.txt`

## Tools Used

- **Amass**
- **Assetfinder**
- **Findomain**
- **Subfinder**
- **Sublist3r**
- **httpx**

## Contributing

Feel free to contribute by opening issues or submitting pull requests to improve this script.

## License

This project is licensed under the MIT License.
