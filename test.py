import os
import sys
import random
import hashlib
import subprocess
from pathlib import Path
import requests
from uuid import uuid4
import winreg
import ctypes

# Function to check if 3rd party antivirus might be blocking the script
def check_3rd_av():
    try:
        # Use WMI to query installed antivirus products
        import wmi
        c = wmi.WMI(namespace="root\\SecurityCenter2")
        av_list = [
            product.displayName
            for product in c.AntiVirusProduct()
            if "windows" not in product.displayName.lower()
        ]
        if av_list:
            print(
                "3rd party Antivirus might be blocking the script - ",
                end="",
                flush=True,
            )
            print(", ".join(av_list), file=sys.stderr)
    except Exception as e:
        print(f"Failed to check for 3rd party antivirus: {e}")

# Function to check if a file exists
def check_file(file_path):
    if not os.path.exists(file_path):
        check_3rd_av()
        print("Failed to create MAS file in temp folder, aborting!")
        print("Help - https://massgrave.dev/troubleshoot")
        sys.exit(1)

# Function to check if running as admin
def is_admin():
    try:
        # Check if the current process has admin privileges
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

# Main script logic
def main():
    # Check if running as admin
    running_as_admin = is_admin()

    if not running_as_admin:
        print("This script requires administrative privileges. Please run it as an administrator.")
        sys.exit(1)

    # Define URLs to download the script
    urls = [
        "https://raw.githubusercontent.com/massgravel/Microsoft-Activation-Scripts/37ec96504a2983a5801c43e975ab78c8f9315d2a/MAS/All-In-One-Version-KL/MAS_AIO.cmd",
        "https://dev.azure.com/massgrave/Microsoft-Activation-Scripts/_apis/git/repositories/Microsoft-Activation-Scripts/items?path=/MAS/All-In-One-Version-KL/MAS_AIO.cmd&versionType=Commit&version=37ec96504a2983a5801c43e975ab78c8f9315d2a",
        "https://git.activated.win/massgrave/Microsoft-Activation-Scripts/raw/commit/37ec96504a2983a5801c43e975ab78c8f9315d2a/MAS/All-In-One-Version-KL/MAS_AIO.cmd",
    ]

    # Shuffle URLs randomly
    random.shuffle(urls)

    # Try downloading the script
    response = None
    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                break
        except Exception:
            continue

    if not response or response.status_code != 200:
        check_3rd_av()
        print("Failed to retrieve MAS from any of the available repositories, aborting!")
        print("Help - https://massgrave.dev/troubleshoot")
        sys.exit(1)

    # Verify script integrity
    release_hash = "49CE81C583C69AC739890D2DFBB908BDD67B862702DAAEBCD2D38F1DDCEE863D"
    script_content = response.content
    hash_object = hashlib.sha256(script_content)
    computed_hash = hash_object.hexdigest().upper()

    if computed_hash != release_hash:
        print(f"Hash ({computed_hash}) mismatch, aborting!")
        print("Report this issue at https://massgrave.dev/troubleshoot")
        sys.exit(1)

    # Save the script to a temporary file
    rand = str(uuid4())
    temp_dir = (
        Path(os.environ["SystemRoot"]) / "Temp"
        if running_as_admin
        else Path(os.environ["USERPROFILE"]) / "AppData" / "Local" / "Temp"
    )
    file_path = temp_dir / f"MAS_{rand}.cmd"
    with open(file_path, "wb") as f:
        f.write(b"@::: " + rand.encode() + b"\r\n" + script_content)

    print(f"Temporary file created at: {file_path}")

    # Check if the file was created successfully
    check_file(file_path)

    # Print the first few lines of the downloaded file
    with open(file_path, "r") as f:
        print("First few lines of the downloaded file:")
        print("\n".join(f.readlines()[:5]))

    # Execute the script
    try:
        print(f"ComSpec environment variable: {os.environ.get('ComSpec')}")
        result = subprocess.run(
            [os.environ["ComSpec"], "/c", f'"{file_path}"'],
            capture_output=True,
            text=True,
        )
        print("STDOUT:", result.stdout)  # Print the standard output
        print("STDERR:", result.stderr)  # Print the standard error
        if result.returncode != 0:  # Check if the command failed
            print("cmd.exe encountered an error.")
            print("Report this issue at https://massgrave.dev/troubleshoot")
        else:
            print("cmd.exe executed successfully.")
    except Exception as e:
        print(f"Failed to execute the script: {e}")

    # Clean up temporary files
    for pattern in ["MAS_*.cmd"]:
        for temp_file in temp_dir.glob(pattern):
            temp_file.unlink()

if __name__ == "__main__":
    main()