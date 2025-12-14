
# admin.py - Enhanced Admin Panel with HWID Reset & GitHub Auto-Push

import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext
import hashlib
import base64
import random
import string
import json
import os
import subprocess
from datetime import datetime, timedelta, timezone

APP_DIR = os.path.dirname(os.path.abspath(__file__))
KEYS_DIR = os.path.join(APP_DIR, "keys")
os.makedirs(KEYS_DIR, exist_ok=True)

KEYS_JSON = os.path.join(APP_DIR, "keys.json")

# ---------------------------
# GitHub Settings (UPDATE THESE)
# ---------------------------
GITHUB_REPO_URL = "https://github.com/D60fps/auth-data.git"  # Your repo URL
GITHUB_BRANCH = "main"
GITHUB_USERNAME = ""  # Set in GUI
GITHUB_TOKEN = ""     # Set in GUI (Personal Access Token)

# ---------------------------
# Helpers
# ---------------------------

def generate_random_key():
    return "-".join(
        "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
        for _ in range(4)
    )

def key_path(key: str):
    return os.path.join(KEYS_DIR, f"{key}.json")

def encode_license(key, expires, hwid):
    data = f"{key}|{expires}|{hwid}"
    encoded = base64.b64encode(data.encode()).decode()
    checksum = hashlib.sha256(encoded.encode()).hexdigest()[:16]
    return f"{encoded}.{checksum}"

def load_all_keys():
    """Load all individual key files"""
    records = []
    for fname in os.listdir(KEYS_DIR):
        if not fname.endswith(".json"):
            continue
        try:
            with open(os.path.join(KEYS_DIR, fname), "r") as f:
                records.append(json.load(f))
        except Exception:
            pass
    return records

def sync_keys_to_central():
    """Sync all individual key files into keys.json"""
    records = load_all_keys()
    central_db = {}
    
    for rec in records:
        key = rec.get("key")
        if key:
            central_db[key] = rec
    
    try:
        with open(KEYS_JSON, "w") as f:
            json.dump(central_db, f, indent=4)
        return True
    except Exception as e:
        print(f"Error syncing to central: {e}")
        return False

def run_git_command(cmd, cwd=None):
    """Run a git command and return output"""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd or APP_DIR,
            capture_output=True,
            text=True,
            shell=True
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

# ---------------------------
# GUI
# ---------------------------

class LicenseGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AXIS SERVICES – KEY AUTH ADMIN")
        self.root.geometry("900x850")
        self.root.configure(bg="#0d0d0d")
        self.root.resizable(False, False)

        self.generated_key_var = tk.StringVar()
        self.duration_var = tk.StringVar(value="7")
        self.hwid_var = tk.StringVar()
        self.github_username_var = tk.StringVar()
        self.github_token_var = tk.StringVar()

        self.setup_gui()
        self.refresh_key_list()

    # ---------------- GUI ----------------

    def setup_gui(self):
        # Header
        top = tk.Frame(self.root, bg="#1a1a1a", height=60)
        top.pack(fill="x")
        tk.Label(
            top,
            text="AXIS SERVICES – ADMIN KEY PANEL",
            fg="white",
            bg="#1a1a1a",
            font=("Segoe UI", 12, "bold")
        ).pack(pady=18)

        # Main body
        body = tk.Frame(self.root, bg="#0d0d0d")
        body.pack(fill="both", expand=True, padx=20, pady=20)

        # GitHub Settings Section
        github_frame = tk.LabelFrame(body, text="GitHub Settings", fg="white", bg="#0d0d0d", font=("Segoe UI", 9, "bold"))
        github_frame.pack(fill="x", pady=(0, 15))

        tk.Label(github_frame, text="GitHub Username", fg="white", bg="#0d0d0d").pack(anchor="w", padx=10, pady=(10, 0))
        tk.Entry(github_frame, textvariable=self.github_username_var, bg="#111", fg="white").pack(fill="x", padx=10)

        tk.Label(github_frame, text="GitHub Token (Personal Access Token)", fg="white", bg="#0d0d0d").pack(anchor="w", padx=10, pady=(10, 0))
        tk.Entry(github_frame, textvariable=self.github_token_var, bg="#111", fg="white", show="*").pack(fill="x", padx=10, pady=(0, 10))

        # Key Generation Section
        gen_frame = tk.LabelFrame(body, text="Key Generation", fg="white", bg="#0d0d0d", font=("Segoe UI", 9, "bold"))
        gen_frame.pack(fill="x", pady=(0, 15))

        tk.Label(gen_frame, text="User HWID", fg="white", bg="#0d0d0d").pack(anchor="w", padx=10, pady=(10, 0))
        tk.Entry(gen_frame, textvariable=self.hwid_var, bg="#111", fg="white").pack(fill="x", padx=10)

        tk.Label(gen_frame, text="Duration (days)", fg="white", bg="#0d0d0d").pack(anchor="w", padx=10, pady=(10, 0))
        tk.Entry(gen_frame, textvariable=self.duration_var, bg="#111", fg="white").pack(fill="x", padx=10)

        tk.Label(gen_frame, text="Generated Key", fg="white", bg="#0d0d0d").pack(anchor="w", padx=10, pady=(10, 0))
        tk.Entry(
            gen_frame,
            textvariable=self.generated_key_var,
            bg="#111",
            fg="#00ff88",
            justify="center",
            state="readonly"
        ).pack(fill="x", padx=10, pady=(0, 10))

        # Action Buttons
        btns = tk.Frame(body, bg="#0d0d0d")
        btns.pack(fill="x", pady=10)

        tk.Button(btns, text="GENERATE KEY", command=self.generate_key, bg="#2a2a2a", fg="white")\
            .pack(side="left", expand=True, fill="x", padx=5)

        tk.Button(btns, text="CREATE LICENSE.DAT", command=self.create_license, bg="#2a2a2a", fg="white")\
            .pack(side="left", expand=True, fill="x", padx=5)

        # Management Buttons
        mgmt_btns = tk.Frame(body, bg="#0d0d0d")
        mgmt_btns.pack(fill="x", pady=5)

        tk.Button(
            mgmt_btns,
            text="RESET HWID",
            bg="#ff8800",
            fg="white",
            command=self.reset_hwid
        ).pack(side="left", expand=True, fill="x", padx=5)

        tk.Button(
            mgmt_btns,
            text="REVOKE KEY",
            bg="#aa0000",
            fg="white",
            command=self.revoke_selected
        ).pack(side="left", expand=True, fill="x", padx=5)

        # GitHub Push Button
        push_frame = tk.Frame(body, bg="#0d0d0d")
        push_frame.pack(fill="x", pady=10)

        tk.Button(
            push_frame,
            text="🚀 SYNC & PUSH TO GITHUB",
            bg="#0066ff",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            command=self.push_to_github,
            height=2
        ).pack(fill="x", padx=5)

        # Key List
        tk.Label(body, text="Active Keys", fg="white", bg="#0d0d0d", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(10, 5))
        
        self.listbox = tk.Listbox(body, bg="#111", fg="white", font=("Consolas", 9), height=15)
        self.listbox.pack(fill="both", expand=True, pady=5)

        # Status Log
        tk.Label(body, text="Status Log", fg="white", bg="#0d0d0d", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(10, 5))
        
        self.log = scrolledtext.ScrolledText(body, bg="#111", fg="#00ff88", font=("Consolas", 8), height=6)
        self.log.pack(fill="x", pady=5)

    # ---------------- Logic ----------------

    def log_message(self, msg):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log.insert(tk.END, f"[{timestamp}] {msg}\n")
        self.log.see(tk.END)
        self.root.update()

    def generate_key(self):
        self.generated_key_var.set(generate_random_key())
        self.log_message(f"Generated key: {self.generated_key_var.get()}")

    def create_license(self):
        key = self.generated_key_var.get()
        hwid = self.hwid_var.get()

        if not key or not hwid:
            messagebox.showerror("Error", "Key and HWID required")
            return

        try:
            days = int(self.duration_var.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid duration")
            return

        now = datetime.now(timezone.utc)
        expires = (now + timedelta(days=days)).isoformat()

        record = {
            "key": key,
            "hwid": None,  # Will be set on first use
            "expires": expires,
            "revoked": False,
            "created": now.isoformat()
        }

        with open(key_path(key), "w") as f:
            json.dump(record, f, indent=4)

        # Sync to central keys.json
        sync_keys_to_central()

        license_data = encode_license(key, expires, hwid)

        self.log_message(f"Created key: {key} (expires in {days} days)")
        
        messagebox.showinfo(
            "SUCCESS",
            f"Key created:\n\n{key}\n\n"
            f"Key file saved to:\nkeys/{key}.json\n\n"
            f"License data created for HWID:\n{hwid}\n\n"
            f"Send the license data to the user."
        )

        self.refresh_key_list()
        self.generated_key_var.set("")
        self.hwid_var.set("")

    def reset_hwid(self):
        """Reset HWID for selected key"""
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Warning", "Please select a key from the list")
            return

        key = self.listbox.get(sel[0]).split(" | ")[0]
        path = key_path(key)

        if not os.path.exists(path):
            messagebox.showerror("Error", "Key file not found")
            return

        with open(path, "r") as f:
            data = json.load(f)

        if data.get("revoked"):
            messagebox.showwarning("Warning", "Cannot reset HWID on revoked key")
            return

        old_hwid = data.get("hwid", "None")
        
        # Reset HWID to None
        data["hwid"] = None
        data["hwid_reset_at"] = datetime.now(timezone.utc).isoformat()

        with open(path, "w") as f:
            json.dump(data, f, indent=4)

        # Sync to central
        sync_keys_to_central()

        self.refresh_key_list()
        self.log_message(f"HWID reset for key: {key}")
        messagebox.showinfo("Success", f"HWID reset for key:\n{key}\n\nOld HWID: {old_hwid}\n\nKey can now be used on a new machine.")

    def revoke_selected(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Warning", "Please select a key from the list")
            return

        key = self.listbox.get(sel[0]).split(" | ")[0]
        path = key_path(key)

        if not os.path.exists(path):
            return

        with open(path, "r") as f:
            data = json.load(f)

        if data.get("revoked"):
            messagebox.showinfo("Info", "Key already revoked.")
            return

        data["revoked"] = True
        data["revoked_at"] = datetime.now(timezone.utc).isoformat()

        with open(path, "w") as f:
            json.dump(data, f, indent=4)

        # Sync to central
        sync_keys_to_central()

        self.refresh_key_list()
        self.log_message(f"Revoked key: {key}")
        messagebox.showinfo("Revoked", f"Key revoked:\n{key}")

    def push_to_github(self):
        """Sync keys and push to GitHub"""
        username = self.github_username_var.get().strip()
        token = self.github_token_var.get().strip()

        if not username or not token:
            messagebox.showerror("Error", "Please enter GitHub username and token")
            return

        self.log_message("Starting GitHub push process...")

        # Step 1: Sync all keys to central keys.json
        self.log_message("Syncing keys to keys.json...")
        if not sync_keys_to_central():
            messagebox.showerror("Error", "Failed to sync keys to central file")
            return

        # Step 2: Initialize git if needed
        self.log_message("Checking git repository...")
        if not os.path.exists(os.path.join(APP_DIR, ".git")):
            self.log_message("Initializing git repository...")
            success, out, err = run_git_command("git init")
            if not success:
                messagebox.showerror("Error", f"Git init failed:\n{err}")
                return

            # Add remote
            repo_url_with_auth = GITHUB_REPO_URL.replace("https://", f"https://{username}:{token}@")
            success, out, err = run_git_command(f'git remote add origin "{repo_url_with_auth}"')
            if not success and "already exists" not in err:
                messagebox.showerror("Error", f"Failed to add remote:\n{err}")
                return

        # Step 3: Configure git
        run_git_command(f'git config user.name "{username}"')
        run_git_command(f'git config user.email "{username}@users.noreply.github.com"')

        # Step 4: Add files
        self.log_message("Adding files to git...")
        success, out, err = run_git_command("git add keys.json keys/")
        if not success:
            messagebox.showerror("Error", f"Git add failed:\n{err}")
            return

        # Step 5: Commit
        self.log_message("Creating commit...")
        commit_msg = f"Update keys - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        success, out, err = run_git_command(f'git commit -m "{commit_msg}"')
        if not success and "nothing to commit" not in out and "nothing to commit" not in err:
            messagebox.showerror("Error", f"Git commit failed:\n{err}")
            return
        elif "nothing to commit" in out or "nothing to commit" in err:
            self.log_message("No changes to commit")
            messagebox.showinfo("Info", "No changes to push - keys are already up to date")
            return

        # Step 6: Push
        self.log_message("Pushing to GitHub...")
        repo_url_with_auth = GITHUB_REPO_URL.replace("https://", f"https://{username}:{token}@")
        success, out, err = run_git_command(f'git push -u origin {GITHUB_BRANCH}')
        
        if not success:
            # Try force push if normal push fails
            self.log_message("Normal push failed, trying force push...")
            success, out, err = run_git_command(f'git push -f origin {GITHUB_BRANCH}')
        
        if success:
            self.log_message("✓ Successfully pushed to GitHub!")
            messagebox.showinfo("Success", "Keys synced and pushed to GitHub successfully!")
        else:
            messagebox.showerror("Error", f"Git push failed:\n{err}")

    def refresh_key_list(self):
        self.listbox.delete(0, tk.END)
        for rec in load_all_keys():
            status = "REVOKED" if rec["revoked"] else "ACTIVE"
            exp = rec["expires"][:10]
            hwid = rec.get("hwid", "None")
            hwid_display = hwid[:16] + "..." if hwid and len(hwid) > 16 else hwid or "Not Set"
            
            self.listbox.insert(
                tk.END,
                f"{rec['key']} | {status} | Exp: {exp} | HWID: {hwid_display}"
            )

# ---------------------------
# Run
# ---------------------------

if __name__ == "__main__":
    root = tk.Tk()
    LicenseGeneratorGUI(root)
    root.mainloop()