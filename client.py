# AXIS Macro Controller - Fixed All Errors
# Python 3.12.0 Complete Version
import urllib.request
import urllib.error
import tkinter as tk
from tkinter import messagebox
import threading
import keyboard
import time
import hashlib
import base64
import os
import json
from datetime import datetime, timezone
import platform
import uuid
import socket
import subprocess
import sys
import ctypes
from typing import Callable

# Try to import win32api for extended mouse support
try:
    import win32api
    import win32con
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False


# ---------------------------
# Admin Check
# ---------------------------
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def run_as_admin():
    if not is_admin():
        try:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
        except Exception:
            pass
        sys.exit()

if not is_admin():
    run_as_admin()


if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
    os.chdir(application_path)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))


# ---------------------------
# GitHub Sync
# ---------------------------
KEY_DB_FILE = os.path.join(application_path, "keys.json")
KEYS_REMOTE_URL = "https://raw.githubusercontent.com/D60fps/auth-data/main/keys.json"

def _load_keys():
    """Load keys from local keys.json"""
    if not os.path.exists(KEY_DB_FILE):
        return {}
    try:
        with open(KEY_DB_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def _save_keys(data):
    """Save keys to local keys.json"""
    try:
        with open(KEY_DB_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception:
        pass

def sync_keys_from_github():
    """Download latest keys.json from GitHub - with fallback"""
    try:
        print(f"Attempting to sync from: {KEYS_REMOTE_URL}")
        with urllib.request.urlopen(KEYS_REMOTE_URL, timeout=10) as response:
            data = response.read()

        with open(KEY_DB_FILE, "wb") as f:
            f.write(data)

        print("Successfully synced keys from GitHub")
        return True
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print("GitHub keys.json not found (404). This is normal on first setup.")
            print("The client will work locally. Push keys from Key_generator.py to GitHub.")
            # Create empty keys.json if it doesn't exist
            if not os.path.exists(KEY_DB_FILE):
                _save_keys({})
            return False
        else:
            print(f"HTTP Error {e.code}: {e.reason}")
            return False
    except urllib.error.URLError as e:
        print(f"Network error: {e.reason}")
        return False
    except Exception as e:
        print(f"Failed to sync keys from GitHub: {e}")
        return False


# ---------------------------
# Mouse Controller
# ---------------------------
class AXISMouseController:
    def __init__(self):
        self.pynput_available = False
        self.controller = None
        self.button_class = None
        self.states = {}
        self._init_pynput()

    def _init_pynput(self):
        try:
            from pynput.mouse import Controller, Button
            self.controller = Controller()
            self.button_class = Button
            self.pynput_available = True
        except Exception:
            class FallbackButton:
                left = 1
                right = 2
                middle = 4
                x1 = 5
                x2 = 6
                x_button1 = 5
                x_button2 = 6
            self.button_class = FallbackButton

    def normalize_button_name(self, button_name: str) -> str:
        if not button_name:
            return ""
        
        name = button_name.lower().strip().replace(' ', '').replace('_', '').replace('-', '')
        
        button_map = {
            'left': 'left', 'leftclick': 'left', 'leftmousebutton': 'left', 
            'mouse1': 'left', 'lmb': 'left', 'leftbutton': 'left', 'lmousebutton': 'left',
            'm1': 'left', 'button1': 'left', 'mousebutton1': 'left',
            
            'right': 'right', 'rightclick': 'right', 'rightmousebutton': 'right', 
            'mouse2': 'right', 'rmb': 'right', 'rightbutton': 'right', 'rmousebutton': 'right',
            'm2': 'right', 'button2': 'right', 'mousebutton2': 'right',
            
            'middle': 'middle', 'middleclick': 'middle', 'middlemousebutton': 'middle', 
            'mouse3': 'middle', 'mmb': 'middle', 'wheel': 'middle', 'middlebutton': 'middle',
            'scrollclick': 'middle', 'wheelclick': 'middle', 'mmousebutton': 'middle',
            'm3': 'middle', 'button3': 'middle', 'mousebutton3': 'middle',
            'wheelbutton': 'middle', 'scrollbutton': 'middle', 'mwheel': 'middle',
            
            'mouse4': 'mouse4', 'x1': 'mouse4', 'sidebutton1': 'mouse4', 
            'back': 'mouse4', 'backward': 'mouse4', 'xbutton1': 'mouse4',
            'mb4': 'mouse4', 'side1': 'mouse4', 'thumb1': 'mouse4',
            'm4': 'mouse4', 'button4': 'mouse4', 'mousebutton4': 'mouse4',
            'xbtn1': 'mouse4', 'backbutton': 'mouse4',
            
            'mouse5': 'mouse5', 'x2': 'mouse5', 'sidebutton2': 'mouse5', 
            'forward': 'mouse5', 'xbutton2': 'mouse5', 'mb5': 'mouse5',
            'side2': 'mouse5', 'thumb2': 'mouse5', 'forwardbutton': 'mouse5',
            'm5': 'mouse5', 'button5': 'mouse5', 'mousebutton5': 'mouse5',
            'xbtn2': 'mouse5',
            
            'mouse6': 'mouse6', 'x3': 'mouse6', 'xbutton3': 'mouse6', 
            'mb6': 'mouse6', 'sidebutton3': 'mouse6', 'm6': 'mouse6',
            'button6': 'mouse6', 'mousebutton6': 'mouse6',
            
            'mouse7': 'mouse7', 'x4': 'mouse7', 'xbutton4': 'mouse7', 
            'mb7': 'mouse7', 'sidebutton4': 'mouse7', 'm7': 'mouse7',
            'button7': 'mouse7', 'mousebutton7': 'mouse7',
            
            'mouse8': 'mouse8', 'x5': 'mouse8', 'xbutton5': 'mouse8', 
            'mb8': 'mouse8', 'sidebutton5': 'mouse8', 'm8': 'mouse8',
            'button8': 'mouse8', 'mousebutton8': 'mouse8',
            
            'mouse9': 'mouse9', 'x6': 'mouse9', 'xbutton6': 'mouse9', 
            'mb9': 'mouse9', 'sidebutton6': 'mouse9', 'm9': 'mouse9',
            'button9': 'mouse9', 'mousebutton9': 'mouse9',
            
            'mouse10': 'mouse10', 'x7': 'mouse10', 'xbutton7': 'mouse10', 
            'mb10': 'mouse10', 'sidebutton7': 'mouse10', 'm10': 'mouse10',
            'button10': 'mouse10', 'mousebutton10': 'mouse10',
        }
        
        return button_map.get(name, "")
    
    def get_button(self, button_name: str):
        if not self.button_class:
            return None
        
        normalized = self.normalize_button_name(button_name)
        
        button_map = {
            'left': self.button_class.left,
            'right': self.button_class.right,
            'middle': self.button_class.middle,
            'mouse4': getattr(self.button_class, 'x1', getattr(self.button_class, 'x_button1', 5)),
            'mouse5': getattr(self.button_class, 'x2', getattr(self.button_class, 'x_button2', 6)),
            'mouse6': 7,
            'mouse7': 8,
            'mouse8': 9,
            'mouse9': 10,
            'mouse10': 11,
        }
        
        return button_map.get(normalized)
    
    def press(self, button_name: str) -> bool:
        normalized = self.normalize_button_name(button_name)
        if not normalized:
            return False
            
        if self.states.get(normalized):
            return True

        button = self.get_button(button_name)
        if button is None:
            return False

        try:
            if self.pynput_available and self.controller:
                if normalized in ['left', 'right', 'middle']:
                    self.controller.press(button)
                    self.states[normalized] = True
                    return True
                elif normalized in ['mouse4', 'mouse5'] and WIN32_AVAILABLE:
                    try:
                        XBUTTON1 = getattr(win32con, 'XBUTTON1', 1)
                        XBUTTON2 = getattr(win32con, 'XBUTTON2', 2)
                        MOUSEEVENTF_XDOWN = getattr(win32con, 'MOUSEEVENTF_XDOWN', 0x0100)
                        
                        button_events = {
                            'mouse4': (MOUSEEVENTF_XDOWN, XBUTTON1),
                            'mouse5': (MOUSEEVENTF_XDOWN, XBUTTON2),
                        }
                        
                        if normalized in button_events:
                            event, xbutton = button_events[normalized]
                            pos = win32api.GetCursorPos()
                            win32api.mouse_event(event, pos[0], pos[1], xbutton, 0)
                            self.states[normalized] = True
                            return True
                    except Exception:
                        pass
                else:
                    try:
                        self.controller.press(button)
                        self.states[normalized] = True
                        return True
                    except Exception:
                        pass
            
            return False
        except Exception:
            return False

    def release(self, button_name: str) -> bool:
        normalized = self.normalize_button_name(button_name)
        if not normalized:
            return False
            
        if not self.states.get(normalized):
            return True

        button = self.get_button(button_name)
        if button is None:
            return False

        try:
            if self.pynput_available and self.controller:
                if normalized in ['left', 'right', 'middle']:
                    self.controller.release(button)
                    self.states[normalized] = False
                    return True
                elif normalized in ['mouse4', 'mouse5'] and WIN32_AVAILABLE:
                    try:
                        XBUTTON1 = getattr(win32con, 'XBUTTON1', 1)
                        XBUTTON2 = getattr(win32con, 'XBUTTON2', 2)
                        MOUSEEVENTF_XUP = getattr(win32con, 'MOUSEEVENTF_XUP', 0x0101)
                        button_events = {
                            'mouse4': (MOUSEEVENTF_XUP, XBUTTON1),
                            'mouse5': (MOUSEEVENTF_XUP, XBUTTON2),
                        }
                        
                        if normalized in button_events:
                            event, xbutton = button_events[normalized]
                            pos = win32api.GetCursorPos()
                            win32api.mouse_event(event, pos[0], pos[1], xbutton, 0)
                            self.states[normalized] = False
                            return True
                    except Exception:
                        pass
                else:
                    try:
                        self.controller.release(button)
                        self.states[normalized] = False
                        return True
                    except Exception:
                        pass
            
            return False
        except Exception:
            return False

    def release_all(self):
        for btn in list(self.states.keys()):
            if self.states.get(btn):
                try:
                    self.release(btn)
                except Exception:
                    pass

mouse_controller = AXISMouseController()


# ---------------------------
# Key Manager
# ---------------------------
class AXISKeyManager:
    def __init__(self):
        self.key_states = {}
        self.mouse_keywords = {
            'mouse', 'left', 'right', 'middle', 'click', 'lmb', 'rmb', 'mmb',
            'x1', 'x2', 'x3', 'x4', 'x5', 'x6', 'x7', 'xbtn', 'xbutton',
            'back', 'forward', 'side', 'thumb', 'button',
            'mouse1', 'mouse2', 'mouse3', 'mouse4', 'mouse5', 
            'mouse6', 'mouse7', 'mouse8', 'mouse9', 'mouse10',
            'wheel', 'scroll', 'mb', 'm1', 'm2', 'm3', 'm4', 'm5',
            'm6', 'm7', 'm8', 'm9', 'm10', 'mwheel'
        }
    
    def is_mouse_button(self, key: str) -> bool:
        if not key:
            return False
        key_lower = key.lower().strip()
        return any(keyword in key_lower for keyword in self.mouse_keywords)
    
    def normalize_key(self, key: str) -> str:
        if not key:
            return ""
        return key.lower().strip()
    
    def press(self, key: str) -> bool:
        if not key:
            return False
        
        normalized = self.normalize_key(key)
        if self.key_states.get(normalized):
            return True
        
        try:
            if self.is_mouse_button(key):
                success = mouse_controller.press(key)
            else:
                keyboard.press(key)
                success = True
            
            if success:
                self.key_states[normalized] = True
            return success
        except Exception:
            return False
    
    def release(self, key: str) -> bool:
        if not key:
            return False
        
        normalized = self.normalize_key(key)
        if not self.key_states.get(normalized):
            return True
        
        try:
            if self.is_mouse_button(key):
                success = mouse_controller.release(key)
            else:
                keyboard.release(key)
                success = True
            
            if success:
                self.key_states[normalized] = False
            return success
        except Exception:
            return False
    
    def is_pressed(self, key: str) -> bool:
        if not key or self.is_mouse_button(key):
            return False
        try:
            return keyboard.is_pressed(key)
        except Exception:
            return False
    
    def release_all(self):
        for key in list(self.key_states.keys()):
            if self.key_states.get(key):
                try:
                    self.release(key)
                except Exception:
                    pass
        mouse_controller.release_all()

key_manager = AXISKeyManager()


# ---------------------------
# Mouse Listener
# ---------------------------
class AXISMouseListener:
    def __init__(self, button_name: str, on_press: Callable, on_release: Callable):
        self.button_name = button_name
        self.on_press_callback = on_press
        self.on_release_callback = on_release
        self.listener = None
        self.running = False
        self.thread = None
        self.is_pressed = False
        self.press_lock = threading.Lock()
        
    def start(self):
        if self.running:
            return
        
        self.running = True
        self.is_pressed = False
        self.thread = threading.Thread(target=self._listen, daemon=True)
        self.thread.start()
    
    def _listen(self):
        try:
            if not mouse_controller.pynput_available:
                return
            
            from pynput.mouse import Listener
            button = mouse_controller.get_button(self.button_name)
            
            if not button:
                return
            
            def on_click(x, y, btn, pressed):
                if not self.running:
                    return False

                try:
                    btn_str = str(btn).lower() if btn is not None else ''
                    button_str = str(button).lower() if button is not None else ''
                except Exception:
                    btn_str = ''
                    button_str = ''

                matched = False
                try:
                    if btn == button:
                        matched = True
                    elif btn_str == button_str:
                        matched = True
                    else:
                        for key in ('left', 'right', 'middle', 'x1', 'x2', 'x_button1', 'x_button2', 'mouse4', 'mouse5'):
                            if key in btn_str and key in button_str:
                                matched = True
                                break
                except Exception:
                    matched = False

                if matched:
                    with self.press_lock:
                        try:
                            if pressed and not self.is_pressed:
                                self.is_pressed = True
                                self.on_press_callback()
                            elif not pressed and self.is_pressed:
                                self.is_pressed = False
                                self.on_release_callback()
                        except Exception:
                            pass
            
            with Listener(on_click=on_click) as listener:
                self.listener = listener
                listener.join()
        except Exception:
            pass
    
    def stop(self):
        self.running = False
        self.is_pressed = False
        if self.listener:
            try:
                self.listener.stop()
            except Exception:
                pass


# ---------------------------
# License System
# ---------------------------
class LicenseManager:
    def __init__(self):
        self.base_dir = application_path
        self.license_file = os.path.join(self.base_dir, "license.dat")
        self._cached_hwid = None
    
    def _get_mac(self):
        try:
            node = uuid.getnode()
            if (node >> 40) & 0x01:
                return None
            return ':'.join(('%012X' % node)[i:i+2] for i in range(0, 12, 2))
        except Exception:
            return None

    def _get_hostname(self):
        try:
            return socket.gethostname()
        except Exception:
            return None

    def _get_platform_info(self):
        try:
            u = platform.uname()
            parts = [u.system, u.node, u.release, u.version, u.machine, u.processor]
            return '|'.join([p for p in parts if p])
        except Exception:
            return None

    def _get_disk_serial(self):
        try:
            system = platform.system().lower()
            if system == "windows":
                try:
                    out = subprocess.check_output(
                        ["wmic", "diskdrive", "get", "serialnumber"],
                        stderr=subprocess.DEVNULL,
                        timeout=2,
                        creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                    )
                    s = out.decode(errors='ignore')
                    lines = [l.strip() for l in s.splitlines() if l.strip()]
                    if len(lines) >= 2:
                        return lines[1]
                except Exception:
                    pass
            else:
                if os.path.exists("/etc/machine-id"):
                    try:
                        with open("/etc/machine-id", "r") as f:
                            return f.read().strip()
                    except Exception:
                        pass
            return None
        except Exception:
            return None

    def get_hwid(self):
        if self._cached_hwid:
            return self._cached_hwid
            
        parts = []
        try:
            mac = self._get_mac()
            if mac:
                parts.append(mac)
            h = self._get_hostname()
            if h:
                parts.append(h)
            p = self._get_platform_info()
            if p:
                parts.append(p)
            d = self._get_disk_serial()
            if d:
                parts.append(d)
        except Exception:
            pass
        
        combined = "|".join(parts) if parts else platform.node() or "unknown"
        try:
            hwid = hashlib.sha256(combined.encode("utf-8")).hexdigest()
        except Exception:
            hwid = hashlib.sha256(str(combined).encode("utf-8")).hexdigest()
        
        self._cached_hwid = hwid
        return hwid

    def _encode_license(self, key, expires, hwid):
        data = f"{key}|{expires}|{hwid}"
        encoded = base64.b64encode(data.encode()).decode()
        checksum = hashlib.sha256(encoded.encode()).hexdigest()[:16]
        return f"{encoded}.{checksum}"

    def _decode_license(self, license_data):
        try:
            if not license_data or '.' not in license_data:
                return None
            
            encoded, checksum = license_data.rsplit('.', 1)
            
            expected_checksum = hashlib.sha256(encoded.encode()).hexdigest()[:16]
            if checksum != expected_checksum:
                return None
            
            decoded = base64.b64decode(encoded.encode()).decode()
            parts = decoded.split('|')
            
            if len(parts) != 3:
                return None
            
            return {
                'key': parts[0],
                'expires': parts[1],
                'hwid': parts[2]
            }
        except Exception:
            return None

    def save_license(self, key, expires, hwid=None):
        try:
            if hwid is None:
                hwid = self.get_hwid()
            
            license_data = self._encode_license(key, expires, hwid)
            
            with open(self.license_file, 'w') as f:
                f.write(license_data)
            
            return True
        except Exception:
            return False

    def load_license(self):
        try:
            if not os.path.exists(self.license_file):
                return None

            with open(self.license_file, 'r') as f:
                license_data = f.read().strip()
            
            if not license_data:
                return None
            
            return self._decode_license(license_data)
        except Exception:
            return None

    def delete_license(self):
        try:
            if os.path.exists(self.license_file):
                os.remove(self.license_file)
        except Exception:
            pass

    def _check_key_authority(self, key, hwid):
        keys = _load_keys()

        if key not in keys:
            return False, "Invalid license key"

        record = keys[key]

        if record.get("revoked"):
            return False, "License key has been revoked"

        expires = record.get("expires")
        if not expires:
            return False, "Key has no expiry"

        try:
            exp_dt = datetime.fromisoformat(expires)
            if exp_dt.tzinfo is None:
                exp_dt = exp_dt.replace(tzinfo=timezone.utc)
            if datetime.now(timezone.utc) >= exp_dt:
                return False, "License key expired"
        except Exception:
            return False, "Invalid key expiration"

        stored_hwid = record.get("hwid")
        if stored_hwid is None:
            record["hwid"] = hwid
            _save_keys(keys)
        elif stored_hwid != hwid:
            return False, "License key already used on another PC"

        return True, "OK"

    def validate_license_key(self, license_data_str):
        try:
            if not license_data_str:
                return False, "No license data provided"

            # The license_data_str should be the raw encoded key from the generator
            # Format: base64_encoded_data.checksum
            license_info = self._decode_license(license_data_str)
            if not license_info:
                print(f"DEBUG: Failed to decode license. Input: {license_data_str[:50]}")
                return False, "Invalid license format"

            key = license_info.get("key")
            current_hwid = self.get_hwid()
            
            print(f"DEBUG: Key from license: {key}")
            print(f"DEBUG: Current HWID: {current_hwid}")

            ok, msg = self._check_key_authority(key, current_hwid)
            if not ok:
                return False, msg

            license_hwid = license_info.get("hwid", "")
            if license_hwid and license_hwid != "None" and license_hwid != current_hwid:
                return False, (
                    f"License HWID mismatch\n"
                    f"Your HWID: {current_hwid}\n"
                    f"License HWID: {license_hwid}"
                )

            expires = license_info.get("expires")
            if not expires:
                return False, "No expiration date found"

            exp_dt = datetime.fromisoformat(expires)
            if exp_dt.tzinfo is None:
                exp_dt = exp_dt.replace(tzinfo=timezone.utc)

            now = datetime.now(timezone.utc)
            if now >= exp_dt:
                return False, "License has expired"

            if self.save_license(key, expires, current_hwid):
                days_left = (exp_dt - now).days
                return True, f"License activated successfully!\nExpires in {days_left} days"
            else:
                return False, "Failed to save license"

        except Exception as e:
            print(f"DEBUG: Exception in validate_license_key: {e}")
            return False, f"Validation error: {str(e)}"

    def is_license_valid(self):
        try:
            # Try to sync, but don't fail if it doesn't work
            sync_keys_from_github()
            
            license_info = self.load_license()
            if not license_info:
                return False

            current_hwid = self.get_hwid()
            license_hwid = license_info.get('hwid')
            
            if not license_hwid or license_hwid != current_hwid:
                self.delete_license()
                return False

            key = license_info.get('key')
            if not key:
                self.delete_license()
                return False

            ok, _ = self._check_key_authority(key, current_hwid)
            if not ok:
                self.delete_license()
                return False

            expires = license_info.get('expires')
            if not expires:
                self.delete_license()
                return False
                
            try:
                exp_dt = datetime.fromisoformat(expires)
                if exp_dt.tzinfo is None:
                    exp_dt = exp_dt.replace(tzinfo=timezone.utc)
                
                now = datetime.now(timezone.utc)
                
                if now >= exp_dt:
                    self.delete_license()
                    return False
                
            except Exception:
                self.delete_license()
                return False

            return True
        except Exception:
            return False


# ---------------------------
# ACTIVATION WINDOW
# ---------------------------
class ActivationWindow:
    def __init__(self, root, on_success):
        self.root = root
        self.on_success = on_success
        self.license_manager = LicenseManager()

        self.root.title("AXIS SERVICES Activation")
        self.root.geometry("500x600")
        self.root.configure(bg="#000000")
        self.root.resizable(False, False)
        
        self.setup_ui()

    def setup_ui(self):
        main_container = tk.Frame(self.root, bg="#000000")
        main_container.pack(fill='both', expand=True, padx=30, pady=40)

        title = tk.Label(main_container, 
                        text="AXIS SERVICES ACTIVATION", 
                        font=("Arial", 20, "bold"),
                        fg="#ffffff", 
                        bg="#000000")
        title.pack(pady=(0, 30))

        key_label = tk.Label(main_container,
                            text="LICENSE KEY",
                            font=("Arial", 20),
                            fg="#ffffff",
                            bg="#000000")
        key_label.pack(anchor='w', pady=(0, 8))

        input_frame = tk.Frame(main_container, bg="#000000", highlightbackground="#FFFFFF", highlightthickness=1)
        input_frame.pack(fill='x', pady=(0, 25))

        self.license_text = tk.Text(input_frame,
                                   font=("Consolas", 9),
                                   bg="#000000",
                                   fg="#ffffff",
                                   insertbackground="#ffffff",
                                   relief='flat',
                                   bd=0,
                                   wrap=tk.WORD,
                                   height=8)
        self.license_text.pack(fill='both', expand=True, padx=12, pady=12)
        self.license_text.focus()

        signin_btn = tk.Button(main_container,
                              text="Sign in",
                              font=("Arial", 11, "bold"),
                              fg="#ffffff",
                              bg="#9fff5b",
                              activebackground="#9fff5b",
                              activeforeground="#ffffff",
                              relief='flat',
                              bd=0,
                              cursor="hand2",
                              command=lambda: self.root.after(50, self.attempt_activation))
        signin_btn.pack(fill='x', ipady=12, pady=(0, 20))

        hwid_label = tk.Label(main_container,
                             text="YOUR HWID",
                             font=("Arial", 9),
                             fg="#ffffff",
                             bg="#000000")
        hwid_label.pack(anchor='w', pady=(0, 8))

        hwid_frame = tk.Frame(main_container, bg="#FFFFFF", highlightbackground="#000000", highlightthickness=1)
        hwid_frame.pack(fill='x', pady=(0, 15))

        hwid = self.license_manager.get_hwid()
        hwid_display = tk.Entry(hwid_frame,
                               font=("Consolas", 8),
                               bg="#000000",
                               fg="#ffffff",
                               insertbackground="#ffffff",
                               relief='flat',
                               bd=0,
                               justify='center')
        hwid_display.insert(0, hwid)
        hwid_display.config(state='readonly')
        hwid_display.pack(fill='x', padx=12, pady=10)

        self.status_label = tk.Label(main_container,
                                     text="",
                                     font=("Arial", 9),
                                     fg="#ff5555",
                                     bg="#000000",
                                     wraplength=340)
        self.status_label.pack(pady=(10, 0))

    def attempt_activation(self):
        license_data = self.license_text.get('1.0', 'end-1c').strip()
        
        if not license_data:
            self.status_label.config(text="⚠ Please paste your license key", fg="#ff0000")
            return

        success, message = self.license_manager.validate_license_key(license_data)

        if success:
            self.status_label.config(text="✓ " + message, fg="#00ff88")
            self.root.after(1000, self.on_success)
        else:
            self.status_label.config(text="✗ " + message, fg="#ff5555")


# ---------------------------
# MAIN GUI
# ---------------------------
class MacroGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AXIS SERVICES - Macro Controller")
        self.root.geometry("700x650")
        self.root.configure(bg="#0a0a0a")
        self.root.resizable(False, False)
        
        self.drag_key_var = tk.StringVar()
        self.select_key_var = tk.StringVar()
        self.double_edit_drag_var = tk.StringVar()
        self.double_edit_select_var = tk.StringVar()
        self.double_edit_key_var = tk.StringVar()
        self.double_edit_delay_var = tk.DoubleVar(value=6.0)

        self.drag_key = ""
        self.select_key = ""
        self.drag_active = False
        self.drag_thread = None
        self.drag_stop_event = threading.Event()
        self.drag_lock = threading.Lock()
        self.drag_listener = None

        self.double_edit_active = False
        self.double_edit_thread = None
        self.double_edit_stop_event = threading.Event()
        self.double_edit_listener = None
        self.double_edit_key = ""
        self.double_edit_drag = ""
        self.double_edit_select = ""
        self.double_edit_lock = threading.Lock()

        self.keyboard_hooks = set()
        self.last_config = ("", "", "", "", "")
        self.shutting_down = False

        self.drag_status_label = None
        self.double_edit_status_label = None
        self.delay_val_label = None

        self.setup_gui()

        threading.Thread(target=self.config_watcher, daemon=True).start()
        threading.Thread(target=self.status_updater, daemon=True).start()
        threading.Thread(target=self.license_checker, daemon=True).start()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_gui(self):
        """Setup the main GUI components"""
        main_frame = tk.Frame(self.root, bg="#0a0a0a")
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)

        title = tk.Label(main_frame, text="AXIS SERVICES - Macro Controller", 
                        font=("Arial", 16, "bold"), fg="#9fff5b", bg="#0a0a0a")
        title.pack(pady=(0, 20))

        # Drag Select Section
        drag_frame = tk.LabelFrame(main_frame, text="DRAG SELECT", 
                                   font=("Arial", 10, "bold"), 
                                   fg="#9fff5b", bg="#1a1a1a", padx=10, pady=10)
        drag_frame.pack(fill='x', pady=(0, 15))

        tk.Label(drag_frame, text="Trigger Key:", fg="#ffffff", bg="#1a1a1a").pack(anchor='w')
        tk.Entry(drag_frame, textvariable=self.drag_key_var, bg="#2a2a2a", 
                fg="#ffffff", width=30).pack(fill='x', pady=(0, 5))

        tk.Label(drag_frame, text="Select Key:", fg="#ffffff", bg="#1a1a1a").pack(anchor='w')
        tk.Entry(drag_frame, textvariable=self.select_key_var, bg="#2a2a2a", 
                fg="#ffffff", width=30).pack(fill='x', pady=(0, 10))

        btn_frame = tk.Frame(drag_frame, bg="#1a1a1a")
        btn_frame.pack(fill='x')
        tk.Button(btn_frame, text="Start", command=self.bind_drag_select, 
                 bg="#9fff5b", fg="#000000", width=15).pack(side='left', padx=(0, 5))
        tk.Button(btn_frame, text="Stop", command=self.stop_drag_select, 
                 bg="#ff5555", fg="#ffffff", width=15).pack(side='left')

        self.drag_status_label = tk.Label(drag_frame, text="Status: Idle", 
                                         fg="#888888", bg="#1a1a1a")
        self.drag_status_label.pack(anchor='w', pady=(10, 0))

        # Double Edit Section
        double_frame = tk.LabelFrame(main_frame, text="DOUBLE EDIT", 
                                     font=("Arial", 10, "bold"), 
                                     fg="#9fff5b", bg="#1a1a1a", padx=10, pady=10)
        double_frame.pack(fill='x', pady=(0, 15))

        tk.Label(double_frame, text="Trigger Key:", fg="#ffffff", bg="#1a1a1a").pack(anchor='w')
        tk.Entry(double_frame, textvariable=self.double_edit_key_var, bg="#2a2a2a", 
                fg="#ffffff", width=30).pack(fill='x', pady=(0, 5))

        tk.Label(double_frame, text="Drag Key:", fg="#ffffff", bg="#1a1a1a").pack(anchor='w')
        tk.Entry(double_frame, textvariable=self.double_edit_drag_var, bg="#2a2a2a", 
                fg="#ffffff", width=30).pack(fill='x', pady=(0, 5))

        tk.Label(double_frame, text="Select Key:", fg="#ffffff", bg="#1a1a1a").pack(anchor='w')
        tk.Entry(double_frame, textvariable=self.double_edit_select_var, bg="#2a2a2a", 
                fg="#ffffff", width=30).pack(fill='x', pady=(0, 5))

        delay_frame = tk.Frame(double_frame, bg="#1a1a1a")
        delay_frame.pack(fill='x', pady=(0, 10))
        tk.Label(delay_frame, text="Delay (s):", fg="#ffffff", bg="#1a1a1a").pack(side='left')
        tk.Scale(delay_frame, from_=0.1, to=20.0, resolution=0.1, 
                variable=self.double_edit_delay_var, bg="#2a2a2a", fg="#9fff5b",
                orient='horizontal').pack(side='left', fill='x', expand=True, padx=(10, 0))
        self.delay_val_label = tk.Label(delay_frame, text="6.0s", fg="#9fff5b", bg="#1a1a1a")
        self.delay_val_label.pack(side='left', padx=(10, 0))

        btn_frame2 = tk.Frame(double_frame, bg="#1a1a1a")
        btn_frame2.pack(fill='x')
        tk.Button(btn_frame2, text="Start", command=self.bind_double_edit, 
                 bg="#9fff5b", fg="#000000", width=15).pack(side='left', padx=(0, 5))
        tk.Button(btn_frame2, text="Stop", command=self.stop_double_edit, 
                 bg="#ff5555", fg="#ffffff", width=15).pack(side='left')

        self.double_edit_status_label = tk.Label(double_frame, text="Status: Idle", 
                                                 fg="#888888", bg="#1a1a1a")
        self.double_edit_status_label.pack(anchor='w', pady=(10, 0))

    def status_updater(self):
        """Update status labels periodically"""
        while not self.shutting_down:
            try:
                if self.delay_val_label:
                    delay = self.double_edit_delay_var.get()
                    self.delay_val_label.config(text=f"{delay:.1f}s")
                time.sleep(0.1)
            except Exception:
                pass

    def config_watcher(self):
        """Watch for configuration changes"""
        while not self.shutting_down:
            try:
                current = (
                    self.drag_key_var.get(),
                    self.select_key_var.get(),
                    self.double_edit_key_var.get(),
                    self.double_edit_drag_var.get(),
                    self.double_edit_select_var.get(),
                )
                if current != self.last_config:
                    self.last_config = current
                time.sleep(0.5)
            except Exception:
                pass

    def license_checker(self):
        """Periodically check license validity"""
        while not self.shutting_down:
            try:
                license_mgr = LicenseManager()
                if not license_mgr.is_license_valid():
                    self.on_closing()
                time.sleep(30)
            except Exception:
                pass

    def normalize(self, key: str) -> str:
        """Normalize key name"""
        return key.lower().strip() if key else ""

    def is_mouse_button(self, key: str) -> bool:
        """Check if key is a mouse button"""
        return key_manager.is_mouse_button(key)

    def bind_drag_select(self):
        """Bind and start drag select macro"""
        with self.drag_lock:
            self.drag_key = self.normalize(self.drag_key_var.get())
            self.select_key = self.normalize(self.select_key_var.get())
            
            if not self.drag_key or not self.select_key:
                if self.drag_status_label:
                    self.drag_status_label.config(text="Status: Missing keys", fg="#ff5555")
                return
            
            if self.drag_active:
                return
            
            self.drag_active = True
            self.drag_stop_event.clear()
            self.drag_thread = threading.Thread(target=self.drag_select_loop, daemon=True)
            self.drag_thread.start()
            if self.drag_status_label:
                self.drag_status_label.config(text="Status: Active", fg="#00ff88")

    def on_drag_press(self):
        """Handle drag key press"""
        if self.drag_active and self.drag_key and self.select_key:
            try:
                key_manager.press(self.select_key)
            except Exception:
                pass

    def on_drag_release(self):
        """Handle drag key release"""
        if self.drag_active and self.select_key:
            try:
                key_manager.release(self.select_key)
            except Exception:
                pass

    def drag_select_loop(self):
        """Main drag select loop"""
        try:
            if self.drag_key and not self.is_mouse_button(self.drag_key):
                listener = AXISMouseListener(self.drag_key, self.on_drag_press, self.on_drag_release)
                self.drag_listener = listener
                listener.start()
                while self.drag_active and not self.drag_stop_event.is_set():
                    time.sleep(0.1)
                listener.stop()
            else:
                while self.drag_active and not self.drag_stop_event.is_set():
                    time.sleep(0.1)
        except Exception:
            pass

    def stop_drag_select(self):
        """Stop drag select macro"""
        with self.drag_lock:
            self.drag_active = False
            self.drag_stop_event.set()
            if self.drag_listener:
                try:
                    self.drag_listener.stop()
                except Exception:
                    pass
            if self.drag_status_label:
                self.drag_status_label.config(text="Status: Idle", fg="#888888")

    def bind_double_edit(self):
        """Bind and start double edit macro"""
        with self.double_edit_lock:
            self.double_edit_key = self.normalize(self.double_edit_key_var.get())
            self.double_edit_drag = self.normalize(self.double_edit_drag_var.get())
            self.double_edit_select = self.normalize(self.double_edit_select_var.get())
            
            if not all([self.double_edit_key, self.double_edit_drag, self.double_edit_select]):
                if self.double_edit_status_label:
                    self.double_edit_status_label.config(text="Status: Missing keys", fg="#ff5555")
                return
            
            if self.double_edit_active:
                return
            
            self.double_edit_active = True
            self.double_edit_stop_event.clear()
            self.double_edit_thread = threading.Thread(target=self.double_edit_loop, daemon=True)
            self.double_edit_thread.start()
            if self.double_edit_status_label:
                self.double_edit_status_label.config(text="Status: Active", fg="#00ff88")

    def on_double_edit_press(self):
        """Handle double edit key press"""
        pass

    def on_double_edit_release(self):
        """Handle double edit key release"""
        if self.double_edit_active and self.double_edit_drag and self.double_edit_select:
            try:
                delay = self.double_edit_delay_var.get()
                key_manager.press(self.double_edit_drag)
                key_manager.press(self.double_edit_select)
                time.sleep(delay)
                key_manager.release(self.double_edit_select)
                key_manager.release(self.double_edit_drag)
            except Exception:
                pass

    def double_edit_loop(self):
        """Main double edit loop"""
        try:
            listener = AXISMouseListener(self.double_edit_key, 
                                        self.on_double_edit_press, 
                                        self.on_double_edit_release)
            self.double_edit_listener = listener
            listener.start()
            while self.double_edit_active and not self.double_edit_stop_event.is_set():
                time.sleep(0.1)
            listener.stop()
        except Exception:
            pass

    def stop_double_edit(self):
        """Stop double edit macro"""
        with self.double_edit_lock:
            self.double_edit_active = False
            self.double_edit_stop_event.set()
            if self.double_edit_listener:
                try:
                    self.double_edit_listener.stop()
                except Exception:
                    pass
            if self.double_edit_status_label:
                self.double_edit_status_label.config(text="Status: Idle", fg="#888888")

    def on_closing(self):
        """Handle window closing"""
        self.shutting_down = True
        self.stop_drag_select()
        self.stop_double_edit()
        key_manager.release_all()
        mouse_controller.release_all()
        try:
            self.root.destroy()
        except Exception:
            pass


# ---------------------------
# Main Entry Point
# ---------------------------
def main():
    try:
        # Try to sync keys from GitHub on startup (not critical)
        print("AXIS SERVICES - Macro Controller Starting...")
        sync_keys_from_github()
        
        license_mgr = LicenseManager()

        if license_mgr.is_license_valid():
            print("Valid license found. Starting Macro Controller...")
            root = tk.Tk()
            MacroGUI(root)
            root.mainloop()
            return

        print("No valid license found. Showing activation window...")
        activation_root = tk.Tk()

        def on_activation_success():
            try:
                activation_root.destroy()
            except Exception:
                pass
            root = tk.Tk()
            MacroGUI(root)
            root.mainloop()

        ActivationWindow(activation_root, on_activation_success)
        activation_root.mainloop()

    except Exception as e:
        print(f"Critical error: {e}")
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Critical Error",
                f"A critical error occurred:\n\n{str(e)}"
            )
        except Exception:
            pass


if __name__ == "__main__":
    main()