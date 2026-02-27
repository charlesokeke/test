import os

DEFAULT_WINDOWS_ACCOUNTS = {
    "administrator",
    "default",
    "defaultaccount",
    "guest",
    "public",
    "wdagutilityaccount",
    "all users",
    "default user",
}

def list_extension_folders():
    users_dir = os.path.join(os.environ.get("SystemDrive", "C:"), "\\Users")

    browser_extension_paths = {
        "Chrome": os.path.join("AppData", "Local", "Google", "Chrome", "User Data", "Default", "Extensions"),
        "Edge":   os.path.join("AppData", "Local", "Microsoft", "Edge", "User Data", "Default", "Extensions"),
    }

    if not os.path.isdir(users_dir):
        print(f"[ERROR] Users directory not found: {users_dir}")
        return

    for user_folder in os.listdir(users_dir):
        user_path = os.path.join(users_dir, user_folder)

        if not os.path.isdir(user_path):
            continue

        if user_folder.strip().lower() in DEFAULT_WINDOWS_ACCOUNTS:
            continue

        for browser, rel_path in browser_extension_paths.items():
            extensions_dir = os.path.join(user_path, rel_path)

            if not os.path.isdir(extensions_dir):
                continue

            ext_folders = [
                f for f in os.listdir(extensions_dir)
                if os.path.isdir(os.path.join(extensions_dir, f))
            ]

            if not ext_folders:
                print(f"[{browser}] {user_folder}: No extensions found.")
                continue

            print(f"\n[{browser}] User: {user_folder}")
            print(f"  Extensions path: {extensions_dir}")
            for folder in ext_folders:
                print(f"    - {folder}")


if __name__ == "__main__":
    list_extension_folders()
