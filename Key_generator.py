import tkinter as tk
from tkinter import messagebox, scrolledtext
import hashlib
import base64
import random
import string
import json
import os
import subprocess
from datetime import datetime, timedelta, timezone
import threading
import webbrowser

APP_DIR = os.path.dirname(os.path.abspath(__file__))
KEYS_DIR = os.path.join(APP_DIR, "keys")
os.makedirs(KEYS_DIR, exist_ok=True)

KEYS_JSON = os.path.join(APP_DIR, "keys.json")

def generate_random_key():
    return "-".join(
        "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
        for _ in range(4)
    )

def key_path(key: str):
    return os.path.join(KEYS_DIR, f"{key}.json")

def load_all_keys():
    """Load all individual key files"""
    records = []
    if not os.path.exists(KEYS_DIR):
        return records
    
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
            shell=True,
            timeout=15,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

class LicenseGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AXIS SERVICES – KEY AUTH ADMIN")
        self.root.geometry("950x900")
        self.root.configure(bg="#0d0d0d")
        self.root.resizable(True, True)

        self.generated_key_var = tk.StringVar()
        self.duration_var = tk.StringVar(value="7")
        self.hwid_var = tk.StringVar()
        self.github_username_var = tk.StringVar()
        self.github_token_var = tk.StringVar()
        self.github_repo_var = tk.StringVar(value="D60fps/auth-data")

        self.setup_gui()
        self.refresh_key_list()

    def setup_gui(self):
        # Header
        top = tk.Frame(self.root, bg="#1a1a1a", height=60)
        top.pack(fill="x")
        tk.Label(
            top,
            text="AXIS SERVICES – ADMIN KEY PANEL",
            fg="#9fff5b",
            bg="#1a1a1a",
            font=("Segoe UI", 14, "bold")
        ).pack(pady=18)

        # Main body
        body = tk.Frame(self.root, bg="#0d0d0d")
        body.pack(fill="both", expand=True, padx=20, pady=20)

        # GitHub Settings Section
        github_frame = tk.LabelFrame(body, text="GitHub Settings", fg="#9fff5b", bg="#1a1a1a", font=("Segoe UI", 9, "bold"), padx=10, pady=10)
        github_frame.pack(fill="x", pady=(0, 15))

        tk.Label(github_frame, text="GitHub Username", fg="white", bg="#1a1a1a").pack(anchor="w", pady=(5, 0))
        tk.Entry(github_frame, textvariable=self.github_username_var, bg="#111", fg="white", width=40).pack(fill="x", pady=(0, 10))

        tk.Label(github_frame, text="GitHub Token (Personal Access Token)", fg="white", bg="#1a1a1a").pack(anchor="w", pady=(5, 0))
        tk.Entry(github_frame, textvariable=self.github_token_var, bg="#111", fg="white", show="*", width=40).pack(fill="x", pady=(0, 10))

        tk.Label(github_frame, text="Repository (username/repo)", fg="white", bg="#1a1a1a").pack(anchor="w", pady=(5, 0))
        tk.Entry(github_frame, textvariable=self.github_repo_var, bg="#111", fg="white", width=40).pack(fill="x", pady=(0, 10))

        help_btn = tk.Button(
            github_frame,
            text="📖 How to create GitHub Token",
            bg="#555",
            fg="white",
            command=lambda: webbrowser.open("https://github.com/settings/tokens/new?scopes=repo&description=AXIS+Keys"),
            font=("Segoe UI", 8)
        )
        help_btn.pack(anchor="w", pady=(0, 5))

        # Key Generation Section
        gen_frame = tk.LabelFrame(body, text="Key Generation", fg="#9fff5b", bg="#1a1a1a", font=("Segoe UI", 9, "bold"), padx=10, pady=10)
        gen_frame.pack(fill="x", pady=(0, 15))

        tk.Label(gen_frame, text="Duration (days)", fg="white", bg="#1a1a1a").pack(anchor="w", pady=(5, 0))
        tk.Entry(gen_frame, textvariable=self.duration_var, bg="#111", fg="white", width=40).pack(fill="x", pady=(0, 10))

        tk.Label(gen_frame, text="User HWID (optional - leave blank for unbound key)", fg="white", bg="#1a1a1a").pack(anchor="w", pady=(5, 0))
        tk.Entry(gen_frame, textvariable=self.hwid_var, bg="#111", fg="white", width=40).pack(fill="x", pady=(0, 10))

        tk.Label(gen_frame, text="Generated Key", fg="#9fff5b", bg="#1a1a1a", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(5, 0))
        tk.Entry(
            gen_frame,
            textvariable=self.generated_key_var,
            bg="#111",
            fg="#9fff5b",
            justify="center",
            state="readonly",
            font=("Consolas", 11, "bold")
        ).pack(fill="x", pady=(0, 10))

        # Action Buttons
        btns = tk.Frame(body, bg="#0d0d0d")
        btns.pack(fill="x", pady=10)

        tk.Button(btns, text="GENERATE KEY", command=self.generate_key, bg="#9fff5b", fg="#000000", font=("Segoe UI", 9, "bold"))\
            .pack(side="left", expand=True, fill="x", padx=5)

        tk.Button(btns, text="CREATE & SAVE KEY", command=self.create_license, bg="#0066ff", fg="white", font=("Segoe UI", 9, "bold"))\
            .pack(side="left", expand=True, fill="x", padx=5)

        # Management Buttons
        mgmt_btns = tk.Frame(body, bg="#0d0d0d")
        mgmt_btns.pack(fill="x", pady=5)

        tk.Button(
            mgmt_btns,
            text="RESET HWID",
            bg="#ff8800",
            fg="white",
            command=self.reset_hwid,
            font=("Segoe UI", 9, "bold")
        ).pack(side="left", expand=True, fill="x", padx=5)

        tk.Button(
            mgmt_btns,
            text="REVOKE KEY",
            bg="#aa0000",
            fg="white",
            command=self.revoke_selected,
            font=("Segoe UI", 9, "bold")
        ).pack(side="left", expand=True, fill="x", padx=5)

        tk.Button(
            mgmt_btns,
            text="DELETE KEY",
            bg="#660000",
            fg="white",
            command=self.delete_selected,
            font=("Segoe UI", 9, "bold")
        ).pack(side="left", expand=True, fill="x", padx=5)

        tk.Button(
            mgmt_btns,
            text="SHOW LICENSE CODE",
            bg="#0066ff",
            fg="white",
            command=self.show_license_code,
            font=("Segoe UI", 9, "bold")
        ).pack(side="left", expand=True, fill="x", padx=5)

        # GitHub Push Button
        push_frame = tk.Frame(body, bg="#0d0d0d")
        push_frame.pack(fill="x", pady=10)

        tk.Button(
            push_frame,
            text="🚀 SYNC & PUSH TO GITHUB",
            bg="#0066ff",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            command=self.push_to_github_threaded,
            height=2
        ).pack(fill="x", padx=5)

        # Key List
        list_frame = tk.Frame(body, bg="#0d0d0d")
        list_frame.pack(fill="both", expand=True, pady=(10, 5))

        tk.Label(list_frame, text="Active Keys", fg="#9fff5b", bg="#0d0d0d", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 5))
        
        scroll = tk.Scrollbar(list_frame)
        scroll.pack(side="right", fill="y")
        
        self.listbox = tk.Listbox(list_frame, bg="#111", fg="#9fff5b", font=("Consolas", 9), height=12, yscrollcommand=scroll.set)
        self.listbox.pack(fill="both", expand=True)
        scroll.config(command=self.listbox.yview)

        # Status Log
        log_frame = tk.Frame(body, bg="#0d0d0d")
        log_frame.pack(fill="x", pady=(10, 0))

        tk.Label(log_frame, text="Status Log", fg="#9fff5b", bg="#0d0d0d", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 5))
        
        self.log = scrolledtext.ScrolledText(log_frame, bg="#111", fg="#00ff88", font=("Consolas", 8), height=6, state="normal")
        self.log.pack(fill="x", pady=0)

    def log_message(self, msg):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log.config(state="normal")
        self.log.insert(tk.END, f"[{timestamp}] {msg}\n")
        self.log.see(tk.END)
        self.log.config(state="disabled")
        self.root.update()

    def generate_key(self):
        """Generate a new random key"""
        key = generate_random_key()
        self.generated_key_var.set(key)
        self.log_message(f"✓ Generated key: {key}")

    def create_license(self):
        """Create and save a license key"""
        key = self.generated_key_var.get()
        hwid = self.hwid_var.get().strip() or None

        if not key:
            messagebox.showerror("Error", "Please generate a key first")
            return

        try:
            days = int(self.duration_var.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid duration (must be a number)")
            return

        if days <= 0:
            messagebox.showerror("Error", "Duration must be positive")
            return

        now = datetime.now(timezone.utc)
        expires = (now + timedelta(days=days)).isoformat()

        record = {
            "key": key,
            "hwid": hwid,
            "expires": expires,
            "revoked": False,
            "created": now.isoformat()
        }

        try:
            with open(key_path(key), "w") as f:
                json.dump(record, f, indent=4)
            
            sync_keys_to_central()
            self.refresh_key_list()
            
            self.log_message(f"✓ Saved key: {key} (expires in {days} days)")
            self.log_message(f"  HWID: {hwid or 'Unbound'}")
            
            messagebox.showinfo("SUCCESS", f"Key created and saved:\n\n{key}\n\nExpires in {days} days")
            
            self.generated_key_var.set("")
            self.hwid_var.set("")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save key: {str(e)}")
            self.log_message(f"✗ Error saving key: {str(e)}")

    def reset_hwid(self):
        """Reset HWID for selected key"""
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Warning", "Please select a key from the list")
            return

        key_line = self.listbox.get(sel[0])
        key = key_line.split(" | ")[0].strip()
        path = key_path(key)

        if not os.path.exists(path):
            messagebox.showerror("Error", "Key file not found")
            return

        try:
            with open(path, "r") as f:
                data = json.load(f)

            if data.get("revoked"):
                messagebox.showwarning("Warning", "Cannot reset HWID on revoked key")
                return

            old_hwid = data.get("hwid", "None")
            data["hwid"] = None
            data["hwid_reset_at"] = datetime.now(timezone.utc).isoformat()

            with open(path, "w") as f:
                json.dump(data, f, indent=4)

            sync_keys_to_central()
            self.refresh_key_list()
            
            self.log_message(f"✓ HWID reset for key: {key}")
            messagebox.showinfo("Success", f"HWID reset for:\n{key}\n\nOld HWID: {old_hwid}\n\nKey can now be used on a new machine.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reset HWID: {str(e)}")
            self.log_message(f"✗ Error resetting HWID: {str(e)}")

    def revoke_selected(self):
        """Revoke selected key"""
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Warning", "Please select a key from the list")
            return

        key_line = self.listbox.get(sel[0])
        key = key_line.split(" | ")[0].strip()
        path = key_path(key)

        if not os.path.exists(path):
            return

        try:
            with open(path, "r") as f:
                data = json.load(f)

            if data.get("revoked"):
                messagebox.showinfo("Info", "Key already revoked.")
                return

            data["revoked"] = True
            data["revoked_at"] = datetime.now(timezone.utc).isoformat()

            with open(path, "w") as f:
                json.dump(data, f, indent=4)

            sync_keys_to_central()
            self.refresh_key_list()
            
            self.log_message(f"✓ Revoked key: {key}")
            messagebox.showinfo("Revoked", f"Key revoked:\n{key}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to revoke key: {str(e)}")
            self.log_message(f"✗ Error revoking key: {str(e)}")

    def delete_selected(self):
        """Delete selected key"""
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Warning", "Please select a key from the list")
            return

        key_line = self.listbox.get(sel[0])
        key = key_line.split(" | ")[0].strip()
        path = key_path(key)

        if not messagebox.askyesno("Confirm", f"Delete key:\n{key}\n\nThis cannot be undone."):
            return

        try:
            if os.path.exists(path):
                os.remove(path)
            
            sync_keys_to_central()
            self.refresh_key_list()
            
            self.log_message(f"✓ Deleted key: {key}")
            messagebox.showinfo("Deleted", f"Key deleted:\n{key}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete key: {str(e)}")
            self.log_message(f"✗ Error deleting key: {str(e)}")

    def push_to_github_threaded(self):
        """Push to GitHub in a separate thread"""
        thread = threading.Thread(target=self.push_to_github, daemon=True)
        thread.start()

    def push_to_github(self):
        """Sync keys and push to GitHub"""
        username = self.github_username_var.get().strip()
        token = self.github_token_var.get().strip()
        repo = self.github_repo_var.get().strip()

        if not username or not token or not repo:
            self.log_message("✗ GitHub username, token, and repository required")
            messagebox.showerror("Error", "Please enter all GitHub credentials")
            return

        self.log_message("🔄 Starting GitHub sync...")
        self.log_message("Step 1: Syncing keys to keys.json...")
        
        if not sync_keys_to_central():
            self.log_message("✗ Failed to sync keys to central file")
            messagebox.showerror("Error", "Failed to sync keys to central file")
            return

        # Check if git repo exists
        git_dir = os.path.join(APP_DIR, ".git")
        
        if not os.path.exists(git_dir):
            self.log_message("Step 2: Initializing git repository...")
            success, out, err = run_git_command("git init")
            if not success:
                self.log_message(f"✗ Git init failed: {err}")
                messagebox.showerror("Error", f"Git init failed:\n{err}")
                return
            
            self.log_message("Step 3: Configuring git...")
            run_git_command(f'git config user.name "{username}"')
            run_git_command(f'git config user.email "{username}@users.noreply.github.com"')
            
            github_url = f"https://{username}:{token}@github.com/{repo}.git"
            self.log_message("Step 4: Adding remote...")
            success, out, err = run_git_command(f'git remote add origin "{github_url}"')
            if not success:
                self.log_message(f"✗ Failed to add remote: {err}")
                messagebox.showerror("Error", f"Failed to add remote:\n{err}")
                return
        else:
            self.log_message("Step 2: Git repo already initialized")
            # Update remote URL in case credentials changed
            github_url = f"https://{username}:{token}@github.com/{repo}.git"
            run_git_command(f'git remote set-url origin "{github_url}"')

        self.log_message("Step 3: Adding files...")
        run_git_command("git add .")

        self.log_message("Step 4: Creating commit...")
        commit_msg = f"Update keys - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        success, out, err = run_git_command(f'git commit -m "{commit_msg}"')
        
        if "nothing to commit" in out.lower() or "nothing to commit" in err.lower():
            self.log_message("ℹ No changes to commit")
        elif not success:
            self.log_message(f"Warning: {err}")

        self.log_message("Step 5: Setting branch to main...")
        run_git_command("git branch -M main")

        self.log_message("Step 6: Fetching from remote...")
        success, out, err = run_git_command("git fetch origin main")
        if not success and "not found" not in err.lower():
            self.log_message(f"Note: {err}")

        self.log_message("Step 7: Pulling remote changes...")
        success, out, err = run_git_command("git pull origin main --allow-unrelated-histories")
        if not success and "no changes added" not in err.lower():
            self.log_message(f"Note: Pulling changes - {err}")

        self.log_message("Step 8: Pushing to GitHub...")
        success, out, err = run_git_command("git push -u origin main")
        
        if success or "Everything up-to-date" in out:
            self.log_message("✓ Successfully pushed to GitHub!")
            messagebox.showinfo("Success", "✓ Keys synced and pushed to GitHub!")
        else:
            # Try force push as fallback
            self.log_message("Note: Attempting force push...")
            success, out, err = run_git_command("git push -f origin main")
            
            if success or "Everything up-to-date" in out:
                self.log_message("✓ Successfully force-pushed to GitHub!")
                messagebox.showinfo("Success", "✓ Keys synced and pushed to GitHub (force)!")
            else:
                self.log_message(f"✗ Push failed: {err}")
                self.log_message("💡 Make sure the repository exists at: https://github.com/" + repo)
                messagebox.showerror("Error", f"Git push failed:\n{err}\n\nMake sure repository exists: https://github.com/{repo}")

    def refresh_key_list(self):
        """Refresh the key list display"""
        self.listbox.delete(0, tk.END)
        records = load_all_keys()
        
        if not records:
            self.listbox.insert(tk.END, "No keys created yet")
            return
        
        for rec in records:
            status = "REVOKED" if rec.get("revoked") else "ACTIVE"
            exp = rec.get("expires", "Unknown")[:10]
            hwid = rec.get("hwid")
            hwid_display = hwid[:16] + "..." if hwid and len(hwid) > 16 else hwid or "Unbound"
            
            self.listbox.insert(
                tk.END,
                f"{rec['key']} | {status} | Exp: {exp} | HWID: {hwid_display}"
            )

    def show_license_code(self):
        """Show the encoded license code for the user to copy"""
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Warning", "Please select a key from the list")
            return

        key_line = self.listbox.get(sel[0])
        key = key_line.split(" | ")[0].strip()
        path = key_path(key)

        if not os.path.exists(path):
            messagebox.showerror("Error", "Key file not found")
            return

        try:
            with open(path, "r") as f:
                data = json.load(f)

            key = data.get("key")
            expires = data.get("expires")
            hwid = data.get("hwid") or "None"

            # Encode the license
            license_str = f"{key}|{expires}|{hwid}"
            encoded = base64.b64encode(license_str.encode()).decode()
            checksum = hashlib.sha256(encoded.encode()).hexdigest()[:16]
            license_code = f"{encoded}.{checksum}"

            # Show it in a window
            code_window = tk.Toplevel(self.root)
            code_window.title(f"License Code - {key}")
            code_window.geometry("600x300")
            code_window.configure(bg="#0d0d0d")

            tk.Label(code_window, text="Copy this code and paste it in the client:", 
                    fg="#9fff5b", bg="#0d0d0d", font=("Segoe UI", 10, "bold")).pack(pady=10)

            code_frame = tk.Frame(code_window, bg="#111", highlightbackground="#9fff5b", highlightthickness=1)
            code_frame.pack(fill="both", expand=True, padx=20, pady=10)

            code_text = tk.Text(code_frame, bg="#111", fg="#00ff88", font=("Consolas", 9), wrap=tk.WORD)
            code_text.pack(fill="both", expand=True, padx=10, pady=10)
            code_text.insert("1.0", license_code)
            code_text.config(state="disabled")

            btn_frame = tk.Frame(code_window, bg="#0d0d0d")
            btn_frame.pack(fill="x", padx=20, pady=10)

            def copy_to_clipboard():
                self.root.clipboard_clear()
                self.root.clipboard_append(license_code)
                messagebox.showinfo("Copied", "License code copied to clipboard!")

            tk.Button(btn_frame, text="Copy to Clipboard", command=copy_to_clipboard,
                     bg="#9fff5b", fg="#000000", font=("Segoe UI", 9, "bold")).pack(side="left", padx=5)

            tk.Button(btn_frame, text="Close", command=code_window.destroy,
                     bg="#555", fg="white", font=("Segoe UI", 9, "bold")).pack(side="left", padx=5)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to show license code: {str(e)}")
            self.log_message(f"✗ Error: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    LicenseGeneratorGUI(root)
    root.mainloop()