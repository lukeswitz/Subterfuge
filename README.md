<img src="https://github.com/user-attachments/assets/82544040-a80a-4ceb-8b04-0a3cbda5a0c1" height="200">

_**Permutated enumeration for elucidating esoteric subdomains**_

## Workflow

1. **Subdomain Discovery**:
    - The included `subTerra.py` [tool](https://github.com/lukeswitz/Subterfuge/blob/main/SubdomainTool/) discovers subdomains using a deep set of tooling.
    - Discovered subdomains are saved in a text file in their respective folders.

2. **Permutation Generation and Validation**:
    - `subterfuge.py` generates patterns and uses them with permutation tools listed below. They are checked with httpx to ensure live domains are saved as the final output.

## Tool Options

### Permutation and Validation
- **AlterX**
- **Gotator**
- **AltDNS**
- **Ripgen**
- **PureDNS**
- **Httpx**
- WIP: **Lepus**

## Usage

> [!NOTE]  
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

### Example Output
(Using only ripgen)
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
Using subdomain_file: /results/glassdoor.com/subdomains.txt
Number of subdomains: 64
Number of patterns: 12
Running ripgen...
ripgen finished - Total Permutations: 26253
Checking which subdomains are live...
Checking subdomains: 100%|████████████████████| 26253/26253 [4:39:47<00:00,  1.56subdomain/s]
Live subdomains saved to /results/glassdoor.com/live_subdomains.txt      
Total unique live subdomains found: 16005.                                                   
Runtime: 4:39:48 (hh:mm:ss).                                                                                                                           
```

> [!IMPORTANT]  
> Generated lists of permutations can be large and httpx csn take a long time.
> Disabling httpx will be a feature soon, for now you can exit the tool and use the combined list in the results folder. 

> [!TIP]  
> Disabling tools or using less patterns with gotator and alterx will lower the amount of possible subdomains. 
> You can also tone this down by changing flags in the script commands or commenting out their use in the main function. Or, add your own commands to the list & mod as needed. 


## Contributing

Open issues or submit pull requests to contribute.

## License

Licensed under the MIT License.
