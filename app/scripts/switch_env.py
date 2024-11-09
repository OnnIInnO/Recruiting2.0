import shutil
import os
import argparse


def switch_environment(env_type: str):
    """Switch between local and Azure environments"""
    if env_type not in ["local", "azure"]:
        raise ValueError("Environment must be either 'local' or 'azure'")

    # Path to your project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Source and destination paths
    source = os.path.join(project_root, f".env.{env_type}")
    destination = os.path.join(project_root, ".env")

    # Copy the appropriate .env file
    shutil.copy2(source, destination)
    print(f"Switched to {env_type} environment")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Switch database environment")
    parser.add_argument(
        "environment", choices=["local", "azure"], help="The environment to switch to"
    )

    args = parser.parse_args()
    switch_environment(args.environment)
