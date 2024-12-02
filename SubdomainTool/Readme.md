# SubTerra 
![image](https://github.com/user-attachments/assets/58c8366c-cb93-4196-a424-dc076bc77729)

**Powerful Subdomain Discovery:**

- Each valid subdomain is checked for life using concurrent httpx tasks.
- A final list is stored in a folder for use with Subterfuge, along with a `live_subdomains.txt`. 

## Prerequisites
- `pip` & `python`
    - Subterra will install all other necessary tools if they are not found on the system. 

## Usage

Run the Script with a Domain:

```bash
python3 subTerra.py example.com
```

> [!NOTE]  
> Flags haven't been added yet- to turn off live domain check or enable amass, etc:

#### 1. Disable httpx check
Comment out the line around `170` as shown:

` # live_subdomains = check_live_subdomains(all_subdomains_file, live_subdomains_file)`


#### 2. Toggle tools:
Remove the `#` around line 180 for the amss command for example to enable it. Amass takes a lot of time and API use if configured.

`   # "amass": f"amass....`

## Sample Output
![image](https://github.com/user-attachments/assets/1eccde12-8bbf-433b-a085-791f50a1db75)


- The script will create a folder for the target.
- Discovered subdomains will be saved in the results/example.com/ folder to be used with Subterfuge, etc.
- The resulting `subdomains.txt` combined output will be checked for live status codes using httpx and saved to `live_subdomains.txt`
- Subsequent runs will append any newly found to the existing files. 

## Tools Used

- **Amass**
- **Assetfinder**
- **Findomain**
- **Subfinder**
- **Sublist3r**
- **Httpx**
- **Anew**
- WIP:**DnsGen**

## Contributing

Feel free to contribute by opening issues or submitting pull requests to improve this script.

## License

This project is licensed under the MIT License.

## Disclaimer

The use of this software and any included tools is provided "as is" without any warranties, expressed or implied. The authors and contributors are not responsible for any damages, data loss, or legal issues that may arise from the use or misuse of this repository. Users are advised to comply with all applicable laws and regulations when using the tools provided. By using this software, you agree to hold the authors and contributors harmless from any liability or claims resulting from its use.
