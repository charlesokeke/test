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


def find_extension_paths(extension_id):
    """Find all installed paths for a given extension ID across non-default Windows users."""
    users_dir = os.path.join(os.environ.get("SystemDrive", "C:"), "\\Users")

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

        for browser, rel_path in browser_paths.items():
            full_path = rel_path.replace("{user}", user_path)
            if os.path.isdir(full_path):
                found.append((user_folder, browser, full_path))

    return found, skipped_accounts


def delete_extensions(extension_ids):
    """Delete multiple browser extensions by ID for all non-default users on the machine."""

    total_success  = 0
    total_fail     = 0
    total_skipped  = set()
    not_found_ids  = []

    print(f"\n{'='*60}")
    print(f"  Extension Removal Tool")
    print(f"  Processing {len(extension_ids)} extension ID(s)")
    print(f"{'='*60}")

    for extension_id in extension_ids:
        extension_id = extension_id.strip()

        print(f"\n  Extension ID : {extension_id}")
        print(f"  {'-'*56}")

        matches, skipped = find_extension_paths(extension_id)

        # Accumulate all skipped default accounts across iterations
        total_skipped.update(skipped)

        if not matches:
            print(f"  [INFO] No installations found for this extension ID.")
            not_found_ids.append(extension_id)
            continue

        print(f"  [INFO] Found {len(matches)} installation(s):\n")

        for user, browser, path in matches:
            print(f"    User    : {user}")
            print(f"    Browser : {browser}")
            print(f"    Path    : {path}")

            try:
                shutil.rmtree(path)
                print(f"    Action  : [SUCCESS] Extension directory deleted.\n")
                total_success += 1
            except PermissionError as e:
                print(f"    Action  : [FAILED] Permission denied — {e}\n")
                total_fail += 1
            except Exception as e:
                print(f"    Action  : [FAILED] Unexpected error — {e}\n")
                total_fail += 1

    # Final consolidated summary
    print(f"\n{'='*60}")
    print(f"  FINAL SUMMARY")
    print(f"{'='*60}")
    print(f"  Extension IDs processed : {len(extension_ids)}")
    print(f"  Installations deleted   : {total_success}")
    print(f"  Deletions failed        : {total_fail}")
    print(f"  IDs with no installs    : {len(not_found_ids)}")

    if not_found_ids:
        print(f"\n  Not found IDs:")
        for eid in not_found_ids:
            print(f"    - {eid}")

    if total_skipped:
        print(f"\n  Skipped built-in Windows account(s):")
        for account in sorted(total_skipped):
            print(f"    - {account}")

    print(f"{'='*60}\n")

    if total_fail > 0:
        print("[TIP] Run this script as Administrator to avoid permission errors.\n")


if __name__ == "__main__":
    extension_ids = [
        "jmjflgjpcpepeafmmgdpfkogkghcpiha",
        "aapbdbdomjkkjkaonfhkkikfgjllcleb",
        "nmmhkkegccagdldgiimedpiccmgmieda",
    ]
    delete_extensions(extension_ids)