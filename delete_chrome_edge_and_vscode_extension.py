import os
import sys
import shutil

# Built-in Windows default accounts to skip
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


def is_default_windows_account(username):
    """Return True if the username matches a known built-in Windows account."""
    return username.strip().lower() in DEFAULT_WINDOWS_ACCOUNTS


def find_vscode_extension_paths(extension_id, user_path):
    """
    Find VS Code extension paths for a given user.
    VS Code extension folders are named <extension-id>-<version>, so we match
    by prefix rather than exact folder name (e.g. 'ms-python.python-2024.2.1').
    Returns a list of matching full paths.
    """
    vscode_ext_dir = os.path.join(user_path, ".vscode", "extensions")
    matched_paths = []

    if not os.path.isdir(vscode_ext_dir):
        return matched_paths

    #prefix = extension_id.lower() + "-"
    for folder in os.listdir(vscode_ext_dir):
        folder_path = os.path.join(vscode_ext_dir, folder)
        if os.path.isdir(folder_path) and folder.lower().startswith(extension_id):
            matched_paths.append(folder_path)

    return matched_paths


def find_extension_paths(extension_id):
    """
    Find all installed paths for a given extension ID across non-default
    Windows users for Chrome, Edge, and VS Code.
    """
    users_dir = os.path.join(os.environ.get("SystemDrive", "C:"), "\\Users")

    # Chrome and Edge use exact extension ID as folder name
    browser_paths = {
        "Chrome": os.path.join(
            "{user}", "AppData", "Local", "Google", "Chrome",
            "User Data", "Default", "Extensions", extension_id
        ),
        "Edge": os.path.join(
            "{user}", "AppData", "Local", "Microsoft", "Edge",
            "User Data", "Default", "Extensions", extension_id
        ),
    }

    found = []
    skipped_accounts = []

    if not os.path.isdir(users_dir):
        print(f"[ERROR] Users directory not found: {users_dir}")
        return found, skipped_accounts

    for user_folder in os.listdir(users_dir):
        user_path = os.path.join(users_dir, user_folder)

        if not os.path.isdir(user_path):
            continue

        if is_default_windows_account(user_folder):
            skipped_accounts.append(user_folder)
            continue

        # Check Chrome and Edge (exact folder name match)
        for browser, rel_path in browser_paths.items():
            full_path = rel_path.replace("{user}", user_path)
            if os.path.isdir(full_path):
                found.append((user_folder, browser, full_path))

        # Check VS Code (prefix match to account for version suffix)
        vscode_matches = find_vscode_extension_paths(extension_id, user_path)
        for vscode_path in vscode_matches:
            found.append((user_folder, "VS Code", vscode_path))

    return found, skipped_accounts


def delete_extension(extension_id):
    """
    Delete a browser/editor extension by ID for all non-default users
    on the machine. Supports Chrome, Edge, and VS Code.
    """
    extension_id = extension_id.strip()

    print(f"\n{'='*60}")
    print(f"  Extension Removal Tool")
    print(f"  Extension ID : {extension_id}")
    print(f"  Mode         : LIVE (will delete)")
    print(f"{'='*60}\n")

    matches, skipped = find_extension_paths(extension_id)

    # Report skipped default accounts
    if skipped:
        print(f"[INFO] Skipped {len(skipped)} built-in Windows account(s):")
        for account in skipped:
            print(f"       - {account}")
        print()

    if not matches:
        print("[INFO] No extension installations found for non-default user accounts.")
        return

    print(f"[INFO] Found {len(matches)} installation(s) across non-default user account(s):\n")

    success_count = 0
    fail_count = 0

    for user, application, path in matches:
        print(f"  User        : {user}")
        print(f"  Application : {application}")
        print(f"  Path        : {path}")

        try:
            shutil.rmtree(path)
            print(f"  Action      : [SUCCESS] Extension directory deleted.\n")
            success_count += 1
        except PermissionError as e:
            print(f"  Action      : [FAILED] Permission denied — {e}\n")
            fail_count += 1
        except Exception as e:
            print(f"  Action      : [FAILED] Unexpected error — {e}\n")
            fail_count += 1

    print(f"\n{'='*60}")
    print(f"  SUMMARY")
    print(f"{'='*60}")
    print(f"  Installations deleted : {success_count}")
    print(f"  Deletions failed      : {fail_count}")
    print(f"{'='*60}\n")

    if fail_count > 0:
        print("[TIP] Run this script as Administrator to avoid permission errors.\n")


if __name__ == "__main__":
    ext_id = "efaidnbmnnnibpcajpcglclefindmkaj"
    delete_extension(ext_id)