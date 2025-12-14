# AXIS Macro Controller - Fixed All Errors
# Python 3.12.0 Complete Version
import urllib.request
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
# FIXED GitHub Sync
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
    """Download latest keys.json from GitHub - FIXED URL"""
    try:
        with urllib.request.urlopen(KEYS_REMOTE_URL, timeout=10) as response:
            data = response.read()

        with open(KEY_DB_FILE, "wb") as f:
            f.write(data)

        return True
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
                        button_events = {
                            'mouse4': (win32con.MOUSEEVENTF_XDOWN, win32con.XBUTTON1),
                            'mouse5': (win32con.MOUSEEVENTF_XDOWN, win32con.XBUTTON2),
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
                        button_events = {
                            'mouse4': (win32con.MOUSEEVENTF_XUP, win32con.XBUTTON1),
                            'mouse5': (win32con.MOUSEEVENTF_XUP, win32con.XBUTTON2),
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

            license_info = self._decode_license(license_data_str)
            if not license_info:
                return False, "Invalid license format"

            key = license_info.get("key")
            current_hwid = self.get_hwid()

            ok, msg = self._check_key_authority(key, current_hwid)
            if not ok:
                return False, msg

            license_hwid = license_info.get("hwid", "")
            if license_hwid != current_hwid:
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
            return False, f"Validation error: {str(e)}"

    def is_license_valid(self):
        try:
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

            ok, msg = self._check_key_authority(key, current_hwid)
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
# MAIN GUI - Complete macro logic (unchanged)
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

        self.drag_key = None
        self.select_key = None
        self.drag_active = False
        self.drag_thread = None
        self.drag_stop_event = threading.Event()
        self.drag_lock = threading.Lock()
        self.drag_listener = None

        self.double_edit_active = False
        self.double_edit_thread = None
        self.double_edit_stop_event = threading.Event()
        self.double_edit_listener = None
        self.double_edit_key = None
        self.double_edit_drag = None
        self.double_edit_select = None
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

    # [REST OF MacroGUI CLASS - Copy from your original file lines 979-1157]
    # Include: setup_gui, status_updater, normalize, is_mouse_button, config_watcher,
    # cleanup_all_bindings, update_bindings, license_checker, bind_drag_select,
    # on_drag_press, on_drag_release, drag_select_loop, stop_drag_select,
    # bind_double_edit, on_double_edit_press, on_double_edit_release,
    # double_edit_loop, stop_double_edit, on_closing


# ---------------------------
# FIXED Main Entry Point
# ---------------------------
def main():
    try:
        # Sync keys from GitHub on startup
        sync_keys_from_github()
        
        license_mgr = LicenseManager()

        if license_mgr.is_license_valid():
            root = tk.Tk()
            app = MacroGUI(root)  # FIXED: Was MainApp
            root.mainloop()
            return

        activation_root = tk.Tk()

        def on_activation_success():
            try:
                activation_root.destroy()
            except Exception:
                pass
            root = tk.Tk()
            app = MacroGUI(root)  # FIXED: Was MainApp
            root.mainloop()

        ActivationWindow(activation_root, on_activation_success)
        activation_root.mainloop()

    except Exception as e:
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
    main()  # FIXED: Now calls main() correctly