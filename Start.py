import tkinter as tk
from pynput import keyboard
from datetime import datetime
import os
import ctypes

class BlackKeyLoggerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Keyboard Monitor")
        self.root.geometry("700x500")
        self.root.configure(bg='#000000')
        
        self.log_file = "keyboard_log.txt"
        
        self.caps_lock = False
        self.shift_pressed = False
        self.ctrl_pressed = False
        self.alt_pressed = False
        self.win_pressed = False
        
        self.current_layout = "EN"
        
        self.create_main_interface()
        self.init_log_file()
        
    def get_keyboard_layout(self):
        """Определяет текущую раскладку клавиатуры"""
        try:
            if os.name == 'nt':
                user32 = ctypes.windll.user32
                hwnd = user32.GetForegroundWindow()
                if hwnd:
                    thread_id = user32.GetWindowThreadProcessId(hwnd, None)
                    layout_id = user32.GetKeyboardLayout(thread_id)
                    
                    if layout_id:
                        lang_id = layout_id & 0xFFFF
                        if lang_id == 0x419:
                            return "RU"
                        elif lang_id == 0x409:
                            return "EN"
                
                return "EN"
            else:
                return "EN"
        except Exception as e:
            print(f"Layout detection error: {e}")
            return "EN"
    
    def convert_to_russian(self, key_char, shift_pressed=False, caps_lock=False):
        """Преобразует английские буквы в русские только когда раскладка RU"""
        # Если раскладка английская - возвращаем символ как есть
        if self.current_layout == "EN":
            # Просто применяем правильный регистр
            if shift_pressed != caps_lock:
                return key_char.upper()
            else:
                return key_char.lower()
        
        # Только для русской раскладки делаем преобразование
        russian_map = {
            'q': 'й', 'w': 'ц', 'e': 'у', 'r': 'к', 't': 'е', 'y': 'н', 
            'u': 'г', 'i': 'ш', 'o': 'щ', 'p': 'з', '[': 'х', ']': 'ъ',
            'a': 'ф', 's': 'ы', 'd': 'в', 'f': 'а', 'g': 'п', 'h': 'р', 
            'j': 'о', 'k': 'л', 'l': 'д', ';': 'ж', "'": 'э',
            'z': 'я', 'x': 'ч', 'c': 'с', 'v': 'м', 'b': 'и', 'n': 'т', 
            'm': 'ь', ',': 'б', '.': 'ю', '/': '.'
        }
        
        russian_map_shift = {
            'q': 'Й', 'w': 'Ц', 'e': 'У', 'r': 'К', 't': 'Е', 'y': 'Н',
            'u': 'Г', 'i': 'Ш', 'o': 'Щ', 'p': 'З', '[': 'Х', ']': 'Ъ',
            'a': 'Ф', 's': 'Ы', 'd': 'В', 'f': 'А', 'g': 'П', 'h': 'Р',
            'j': 'О', 'k': 'Л', 'l': 'Д', ';': 'Ж', "'": 'Э',
            'z': 'Я', 'x': 'Ч', 'c': 'С', 'v': 'М', 'b': 'И', 'n': 'Т',
            'm': 'Ь', ',': 'Б', '.': 'Ю', '/': ','
        }
        
        effective_shift = shift_pressed != caps_lock
        
        if effective_shift:
            return russian_map_shift.get(key_char.lower(), key_char.upper())
        else:
            return russian_map.get(key_char.lower(), key_char)
        
    def init_log_file(self):
        try:
            with open(self.log_file, "w", encoding="utf-8") as f:
                f.write("=== Keyboard Monitor Log ===\n")
                f.write(f"Session started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 50 + "\n\n")
        except Exception as e:
            print(f"Error creating log file: {e}")
            
    def create_main_interface(self):
        self.main_frame = tk.Frame(self.root, bg='#000000')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.create_monitor_interface()
        
    def create_monitor_interface(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        title_label = tk.Label(self.main_frame, text="Keyboard Monitor", 
                             font=("Arial", 14, "bold"),
                             bg='#000000', fg='#FFFFFF')
        title_label.pack(pady=5)
        
        self.status_frame = tk.Frame(self.main_frame, bg='#1A1A1A')
        self.status_frame.pack(pady=5, fill=tk.X)
        
        status_labels = [
            ("CapsLock: OFF", "caps_status"),
            ("Shift: OFF", "shift_status"), 
            ("Ctrl: OFF", "ctrl_status"),
            ("Alt: OFF", "alt_status"),
            ("Win: OFF", "win_status"),
            ("Layout: EN", "layout_status")
        ]
        
        self.status_vars = {}
        for text, name in status_labels:
            label = tk.Label(self.status_frame, text=text, bg='#1A1A1A', fg='#FFFFFF', font=("Arial", 9))
            label.pack(side=tk.LEFT, padx=8)
            self.status_vars[name] = label
        
        text_container = tk.Frame(self.main_frame, bg='#000000')
        text_container.pack(pady=10, fill=tk.BOTH, expand=True)
        
        self.text_area = tk.Text(text_container, height=15, width=80, 
                               font=("Consolas", 9), 
                               bg='#1A1A1A', fg='#FFFFFF',
                               insertbackground='#FFFFFF',
                               selectbackground='#404040')
        
        self.scrollbar = tk.Scrollbar(text_container, bg='#404040', troughcolor='#2A2A2A')
        self.text_area.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.text_area.yview)
        
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.button_frame = tk.Frame(self.main_frame, bg='#000000')
        self.button_frame.pack(pady=10)
        
        buttons = [
            ("Start Monitoring", self.start_monitoring),
            ("Stop Monitoring", self.stop_monitoring),
            ("Clear Log", self.clear_log),
            ("Save Log", self.save_log),
            ("Switch Layout", self.switch_layout),
        ]
        
        self.buttons = {}
        for text, command in buttons:
            btn = tk.Button(self.button_frame, text=text, command=command, 
                          bg='#404040', fg='#FFFFFF',
                          activebackground='#606060',
                          activeforeground='#FFFFFF',
                          relief='raised', bd=1, padx=10, pady=5,
                          font=("Arial", 9))
            btn.pack(side=tk.LEFT, padx=5)
            self.buttons[text] = btn
            
        self.buttons["Stop Monitoring"].config(state=tk.DISABLED)
        self.listener = None

    def switch_layout(self):
        """Ручное переключение раскладки"""
        self.current_layout = "RU" if self.current_layout == "EN" else "EN"
        self.update_status_labels()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"{timestamp} - [LAYOUT_SWITCHED] {self.current_layout}\n"
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
        if hasattr(self, 'text_area'):
            self.text_area.insert(tk.END, log_entry)
            self.text_area.see(tk.END)
        
    def update_status_labels(self):
        if not hasattr(self, 'status_vars'):
            return
            
        self.current_layout = self.get_keyboard_layout()
            
        status_map = {
            "caps_status": ("CapsLock", self.caps_lock),
            "shift_status": ("Shift", self.shift_pressed),
            "ctrl_status": ("Ctrl", self.ctrl_pressed),
            "alt_status": ("Alt", self.alt_pressed),
            "win_status": ("Win", self.win_pressed),
            "layout_status": ("Layout", self.current_layout)
        }
        
        for name, (label, state) in status_map.items():
            if name == "layout_status":
                text = f"{label}: {state}"
                color = "#00FFFF"
            else:
                text = f"{label}: {'ON' if state else 'OFF'}"
                color = "#00FF00" if state else "#FF0000"
                
            if name in self.status_vars:
                self.status_vars[name].config(text=text, fg=color)
        
    def get_key_name(self, key):
        key_names = {
            keyboard.Key.space: "SPACE", keyboard.Key.enter: "ENTER", 
            keyboard.Key.backspace: "BACKSPACE", keyboard.Key.tab: "TAB",
            keyboard.Key.esc: "ESC", keyboard.Key.shift: "SHIFT",
            keyboard.Key.shift_r: "SHIFT_R", keyboard.Key.ctrl: "CTRL",
            keyboard.Key.ctrl_r: "CTRL_R", keyboard.Key.alt: "ALT",
            keyboard.Key.alt_r: "ALT_R", keyboard.Key.cmd: "WIN",
            keyboard.Key.cmd_r: "WIN_R", keyboard.Key.up: "UP",
            keyboard.Key.down: "DOWN", keyboard.Key.left: "LEFT",
            keyboard.Key.right: "RIGHT", keyboard.Key.home: "HOME",
            keyboard.Key.end: "END", keyboard.Key.page_up: "PAGE_UP",
            keyboard.Key.page_down: "PAGE_DOWN", keyboard.Key.insert: "INSERT",
            keyboard.Key.delete: "DELETE"
        }
        
        for i in range(1, 13):
            key_names[getattr(keyboard.Key, f'f{i}')] = f'F{i}'
            
        return key_names.get(key, str(key).replace("Key.", "").upper())
        
    def on_press(self, key):
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            old_layout = self.current_layout
            self.current_layout = self.get_keyboard_layout()
            
            if old_layout != self.current_layout:
                log_entry = f"{timestamp} - [LAYOUT_SWITCHED] {old_layout} -> {self.current_layout}\n"
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(log_entry)
                if hasattr(self, 'text_area'):
                    self.text_area.insert(tk.END, log_entry)
                    self.text_area.see(tk.END)
        
            if key == keyboard.Key.caps_lock:
                self.caps_lock = not self.caps_lock
                log_entry = f"{timestamp} - [CAPS_LOCK] {'ON' if self.caps_lock else 'OFF'}\n"
                
            elif key in [keyboard.Key.shift, keyboard.Key.shift_r]:
                self.shift_pressed = True
                log_entry = f"{timestamp} - [SHIFT_PRESSED]\n"
                
            elif key in [keyboard.Key.ctrl, keyboard.Key.ctrl_r]:
                self.ctrl_pressed = True
                log_entry = f"{timestamp} - [CTRL_PRESSED]\n"
                
            elif key in [keyboard.Key.alt, keyboard.Key.alt_r]:
                self.alt_pressed = True
                log_entry = f"{timestamp} - [ALT_PRESSED]\n"
                
            elif key in [keyboard.Key.cmd, keyboard.Key.cmd_r]:
                self.win_pressed = True
                log_entry = f"{timestamp} - [WIN_PRESSED]\n"
                
            elif hasattr(key, 'char') and key.char is not None:
                char = key.char
                
                # ВСЕГДА используем преобразование, но метод теперь умный
                char = self.convert_to_russian(char, self.shift_pressed, self.caps_lock)
                
                modifiers = []
                if self.ctrl_pressed: modifiers.append("CTRL")
                if self.alt_pressed: modifiers.append("ALT") 
                if self.shift_pressed: modifiers.append("SHIFT")
                if self.win_pressed: modifiers.append("WIN")
                
                if modifiers:
                    combo = "+".join(modifiers) + f"+'{char}'"
                    log_entry = f"{timestamp} - [COMBO] {combo} (Layout: {self.current_layout})\n"
                else:
                    log_entry = f"{timestamp} - [KEY] '{char}' (Layout: {self.current_layout})\n"
                    
            else:
                key_name = self.get_key_name(key)
                log_entry = f"{timestamp} - [{key_name}]\n"
            
            if not any([key == keyboard.Key.shift, key == keyboard.Key.shift_r,
                       key == keyboard.Key.ctrl, key == keyboard.Key.ctrl_r,
                       key == keyboard.Key.alt, key == keyboard.Key.alt_r]):
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(log_entry)
                    
                if hasattr(self, 'text_area'):
                    self.text_area.insert(tk.END, log_entry)
                    self.text_area.see(tk.END)
                    self.update_status_labels()
        
        except Exception as e:
            error_msg = f"{timestamp} - Error: {str(e)}\n"
            try:
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(error_msg)
            except:
                pass

    def on_release(self, key):
        try:
            if key in [keyboard.Key.shift, keyboard.Key.shift_r]:
                self.shift_pressed = False
            elif key in [keyboard.Key.ctrl, keyboard.Key.ctrl_r]:
                self.ctrl_pressed = False
            elif key in [keyboard.Key.alt, keyboard.Key.alt_r]:
                self.alt_pressed = False
            elif key in [keyboard.Key.cmd, keyboard.Key.cmd_r]:
                self.win_pressed = False
                
            self.update_status_labels()
            
        except Exception as e:
            pass

    def start_monitoring(self):
        try:
            self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
            self.listener.start()
            self.buttons["Start Monitoring"].config(state=tk.DISABLED)
            self.buttons["Stop Monitoring"].config(state=tk.NORMAL)
            
            start_msg = f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - *** MONITORING STARTED ***\n"
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(start_msg)
                
            self.text_area.insert(tk.END, start_msg)
            
        except Exception as e:
            error_msg = f"Error: {e}\n"
            self.text_area.insert(tk.END, error_msg)
        
    def stop_monitoring(self):
        try:
            if self.listener:
                self.listener.stop()
            self.buttons["Start Monitoring"].config(state=tk.NORMAL)
            self.buttons["Stop Monitoring"].config(state=tk.DISABLED)
            
            stop_msg = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - *** MONITORING STOPPED ***\n"
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(stop_msg)
                
            self.text_area.insert(tk.END, stop_msg)
            
        except Exception as e:
            error_msg = f"Error: {e}\n"
            self.text_area.insert(tk.END, error_msg)
        
    def clear_log(self):
        try:
            self.text_area.delete(1.0, tk.END)
        except Exception as e:
            print(f"Error: {e}")
            
    def save_log(self):
        try:
            filename = f"keyboard_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            content = self.text_area.get(1.0, tk.END)
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            self.text_area.insert(tk.END, f"\nSaved: {filename}\n")
        except Exception as e:
            self.text_area.insert(tk.END, f"Save error: {e}\n")

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = BlackKeyLoggerApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit...")
