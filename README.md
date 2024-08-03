# Subterfuge
_**A comprehensive toolset for subdomain discovery and permutation generation to find esoteric subdomains.**_

## Workflow

1. **Subdomain Discovery**:
    - The included `subTerra.py` [tool](https://github.com/lukeswitz/Subterfuge/blob/main/SubdomainTool/) discovers subdomains using a deep set of tooling.
    - Discovered subdomains are saved in a text file in their respective folders.

2. **Permutation Generation and Validation**:
    - `subterfuge.py` generates patterns and uses them with permutation tools listed below. They are checked with httpx to ensure live domains are saved as the final output.

## Tools

### Permutation and Validation
- **AlterX**
- **Gotator**
- **AltDNS**
- **DnsGen**
- **Ripgen**
- WIP: **Lepus**
- **PureDNS**
- **Httpx**

## Usage

> [!IMPORTANT]  
> A subdomain list is **needed in the subdomains.txt file**
> If you don't use the included subdomain finder tool.
```
├── SubdomainTool
│   ├── results
│   │   └── example.com
│   │       ├── live_subdomains.txt
│   │       ├── subdomains.txt  <---- add if needed
│   └── subTerra.py
├── subterfuge.py

```

### Step 1: Discover Subdomains

Navigate to the `SubdomainTool` directory and run:
```bash
cd SubdomainTool
chmod +x subTerra.py
python3 subTerra.py example.com
```

### Step 2: Generate Permutations and Check Validity

Navigate back to the root directory and run:
```bash
cd ..
chmod +x subterfuge.py
./subterfuge.py example.com
```

Example Output:
```
              8        o                d'b                      
              8        8                8                        
.oPYo. o    o 8oPYo.  o8P .oPYo. oPYo. o8P  o    o .oPYo. .oPYo. 
Yb..   8    8 8    8   8  8oooo8 8  `'  8   8    8 8    8 8oooo8 
  'Yb. 8    8 8    8   8  8.     8      8   8    8 8    8 8.     
`YooP' `YooP' `YooP'   8  `Yooo' 8      8   `YooP' `YooP8 `Yooo' 
:.....::.....::.....:::..::.....:..:::::..:::.....::....8 :.....:
:::::::::::::::::::::::::::::::::::::::::::::::::::::ooP'.:::::::
:::::::::::::::::::::::::::::::::::::::::::::::::::::...:::::::::

Discovery initiated for: glassdoor.com
Using live_subdomains_file: /home/dev/Subterfuge/SubdomainTool/results/glassdoor.com/live_subdomains.txt
Number of subdomains: 110
Number of patterns: 12
Running alterx...
alterx finished - Total Permutations: 1777651
Running gotator...
gotator finished - Total Permutations: 1880364
Running dnsgen...
dnsgen finished - Total Permutations: 1889889
Running ripgen...
ripgen finished - Total Permutations: 1962183
Checking which subdomains are live...
Checking subdomains:   0%|                  | 470/1962183 [03:14<201:58:21,  2.70subdomain/s]
```

> [!WARNING]  
> Generated lists of permutations can be large, into the GB's.
> You can tone this down by simply removing some flags from the script commands.


## Contributing

Open issues or submit pull requests to contribute.

## License

Licensed under the MIT License.
