<img src="https://github.com/user-attachments/assets/82544040-a80a-4ceb-8b04-0a3cbda5a0c1" height="200">

**Discover > Enumerate > Permutate**
 _...elucidating esoteric subdomains_

## Workflow

1. **Subdomain Discovery**:
    - The included `subTerra.py` [tool](https://github.com/lukeswitz/Subterfuge/blob/main/SubdomainTool/) discovers subdomains using a deep set of tooling.
   
     - Discovered subdomains are saved in a text file as well as the verified & live file.
    - Rerunning the tool adds anything new to the existing files. 

2. **Permutation Generation and Validation**:
    - `subterfuge.py` generates patterns and uses them with the tools below.
    - They are checked with `httpx` to ensure live domains are saved as the final output using `anew`. 
    - It will check if the live file exists in the SubdomainTool results directory first, falling back to subdomains.txt. If it's the first run, **the file wont be found unless manually added** as shown below.

## Tools & Use

### Permutation and Validation
- **AlterX**
- **Gotator**
- **AltDNS**
- **Ripgen**
- **PureDNS**
- **Httpx**
- **Anew**
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

![image](https://github.com/user-attachments/assets/d3b71636-10c3-4992-add7-2ed6b3656c15)


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

## Disclaimer

The use of this software and any included tools is provided "as is" without any warranties, expressed or implied. The authors and contributors are not responsible for any damages, data loss, or legal issues that may arise from the use or misuse of this repository. Users are advised to comply with all applicable laws and regulations when using the tools provided. By using this software, you agree to hold the authors and contributors harmless from any liability or claims resulting from its use.
