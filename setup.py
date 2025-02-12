import site
import os
import platform
from project_path import PROJECT_ROOT_DIR, APPS_DIR

def create_conda_pth(paths):
    for path in paths:
        site_packages_dirs = site.getsitepackages()
        if not site_packages_dirs:
            raise RuntimeError("Cannot find site-packages directory.")

        site_packages_dir = site_packages_dirs[0]
        conda_pth_path = os.path.join(site_packages_dir, 'conda.pth')

        with open(conda_pth_path, 'w') as f:
            for path in paths:
                f.write(path + '\n')

        print(f"Created {conda_pth_path} with the following paths:")
        for path in paths:
            print(path)


if __name__ == "__main__":
    # Add the project root directory and each app root directory to the conda environment paths
    create_conda_pth([PROJECT_ROOT_DIR, APPS_DIR])

    # If on Linux, set the browser environment variable
    if platform.system() == "Linux":
        print("Enter the path to your default browser in your WSL environment")
        print("e.g., /mnt/c/Program Files/Google/Chrome/Application/chrome.exe")
        browser_path = input(": ")
        try:
            os.system(f'conda env config vars set BROWSER="{browser_path}"')
        except Exception as e:
            raise Exception("Failed to set the default browser environment variable") from e
