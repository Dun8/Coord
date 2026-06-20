import time
import threading
from collections import deque
from tkinter import filedialog

import customtkinter as ctk
from pynput import mouse, keyboard
from pynput.mouse import Controller
from win32gui import FindWindow, GetWindowRect
import win32gui
from PIL import Image

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

FONT_LARGE = ("Arial", 24, "bold")
FONT_SMALL = ("Arial", 12)
THROTTLE_INTERVAL = 0.02
NOTIFY_DURATION_MS = 5000
COPY_KEYS = {'c', 'с', 'C', 'С'}
HOTKEYS_MAIN = {'v', 'м', 'w', 'ц', 'i', 'ш'}


class App:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Coord")
        self.root.resizable(False, False)

        self.mouse_ctrl = Controller()
        self.coord_var = ctk.StringVar(value=str(self.mouse_ctrl.position))
        self.current_coord = str(self.mouse_ctrl.position)

        self.in_coord_overlay = False
        self.coord_overlay: ctk.CTkToplevel | None = None

        self.window_history: deque[str] = deque(maxlen=2)
        self._last_move_time = 0.0

        self._build_main_ui()
        self._center_window(self.root)
        self._start_listeners()
        threading.Thread(target=self._track_foreground_windows, daemon=True).start()

    def _build_main_ui(self):
        ctk.CTkLabel(
            self.root,
            textvariable=self.coord_var,
            font=ctk.CTkFont(family="Arial", size=24, weight="bold"),
        ).pack(pady=(12, 6), padx=20)

        btn_cfg = dict(width=260, height=36)
        ctk.CTkButton(
            self.root,
            text="Coordinates in a separate window  [V]",
            command=self._open_coord_overlay,
            **btn_cfg,
        ).pack(pady=4, padx=20)
        ctk.CTkButton(
            self.root,
            text="Find out the window coordinates  [W]",
            command=self._show_window_coords,
            **btn_cfg,
        ).pack(pady=4, padx=20)
        ctk.CTkButton(
            self.root,
            text="Open image  [I]",
            command=self._open_image_viewer,
            **btn_cfg,
        ).pack(pady=(4, 14), padx=20)

    def _center_window(self, win: ctk.CTk | ctk.CTkToplevel):
        win.update_idletasks()
        sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
        ww, wh = win.winfo_width(), win.winfo_height()
        win.geometry(f"+{(sw - ww) // 2}+{(sh - wh) // 2}")

    def _screen_size(self):
        return self.root.winfo_screenwidth(), self.root.winfo_screenheight()

    def _set_coord(self, x, y):
        self.current_coord = f"({x}, {y})"
        self.coord_var.set(self.current_coord)

    def _on_mouse_move(self, x, y):
        now = time.monotonic()
        if now - self._last_move_time > THROTTLE_INTERVAL:
            self._last_move_time = now
            self.root.after(0, self._set_coord, x, y)

    def _on_key_press(self, key):
        try:
            ch = key.char
        except AttributeError:
            return

        if not self.in_coord_overlay:
            if ch in ('v', 'м'):
                self.root.after(0, self._open_coord_overlay)
            elif ch in ('w', 'ц'):
                self.root.after(0, self._show_window_coords)
            elif ch in ('i', 'ш'):
                self.root.after(0, self._open_image_viewer)
        else:
            if ch in ('c', 'с'):
                self.root.after(0, self._copy_coord_from_overlay)
            elif ch in ('m', 'ь'):
                self.root.after(0, self._close_coord_overlay)

    def _start_listeners(self):
        mouse.Listener(on_move=self._on_mouse_move).start()
        keyboard.Listener(on_press=self._on_key_press).start()

    def _open_coord_overlay(self):
        if self.in_coord_overlay:
            return
        self.in_coord_overlay = True
        self.root.withdraw()

        ov = ctk.CTkToplevel(self.root)
        ov.title("Coord Overlay")
        ov.attributes("-topmost", True)
        ov.resizable(False, False)
        ov.protocol("WM_DELETE_WINDOW", self._close_coord_overlay)
        self.coord_overlay = ov

        frame = ctk.CTkFrame(ov)
        frame.pack(padx=20, pady=20)

        ctk.CTkLabel(
            frame,
            textvariable=self.coord_var,
            font=ctk.CTkFont(family="Arial", size=24, weight="bold"),
        ).pack(pady=(10, 6))
        ctk.CTkButton(frame, text="Copy coordinates  [C]", command=self._copy_coord_from_overlay, width=220).pack(pady=4)
        ctk.CTkButton(frame, text="Return to main menu  [M]", command=self._close_coord_overlay, width=220).pack(pady=(4, 10))

        def _place():
            ov.update_idletasks()
            sw, sh = self._screen_size()
            ww, wh = ov.winfo_width(), ov.winfo_height()
            ov.geometry(f"+{sw - ww - 10}+{sh - wh - 50}")

        ov.after(50, _place)

    def _close_coord_overlay(self):
        self.in_coord_overlay = False
        if self.coord_overlay and self.coord_overlay.winfo_exists():
            self.coord_overlay.destroy()
        self.coord_overlay = None
        self.root.deiconify()
        self.root.lift()

    def _copy_coord_from_overlay(self):
        win = self.coord_overlay
        if win and win.winfo_exists():
            win.clipboard_clear()
            win.clipboard_append(self.current_coord)

    def _track_foreground_windows(self):
        while True:
            try:
                if not self.root.winfo_exists():
                    break
            except Exception:
                break
            hwnd = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(hwnd)
            if title and (not self.window_history or self.window_history[-1] != title):
                self.window_history.append(title)
            time.sleep(0.1)

    def _show_window_coords(self):
        def task():
            history = list(self.window_history)
            title = history[-2] if len(history) >= 2 else (history[-1] if history else None)
            if not title:
                return

            hwnd = FindWindow(None, title)
            if not hwnd:
                text = f"Window '{title}' not found."
                coords = None
            else:
                rect = GetWindowRect(hwnd)
                text = f'Window coordinates "{title}":\n{rect}'
                coords = str(rect)

            def show():
                if coords:
                    self.root.clipboard_clear()
                    self.root.clipboard_append(coords)

                win = ctk.CTkToplevel(self.root)
                win.title("Window Coords")
                win.attributes("-topmost", True)
                win.resizable(False, False)

                ctk.CTkLabel(win, text=text, font=ctk.CTkFont(family="Arial", size=12)).pack(padx=20, pady=20)

                def _place():
                    win.update_idletasks()
                    sw, _ = self._screen_size()
                    win.geometry(f"+{sw - win.winfo_width() - 10}+10")

                win.after(50, _place)
                self.root.after(NOTIFY_DURATION_MS, lambda: win.destroy() if win.winfo_exists() else None)

            self.root.after(0, show)

        threading.Thread(target=task, daemon=True).start()

    def _open_image_viewer(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg"), ("All files", "*.*")]
        )
        if not filepath:
            return
        if filepath.rsplit(".", 1)[-1].lower() not in ("png", "jpg", "jpeg"):
            return

        try:
            pil_image = Image.open(filepath)
            img = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=pil_image.size)
        except Exception:
            return

        win = ctk.CTkToplevel(self.root)
        win.title("CoordImage")
        win.resizable(False, False)

        coord_label = ctk.CTkLabel(win, text="X: 0,  Y: 0", font=ctk.CTkFont(family="Arial", size=13))
        coord_label.pack(fill="x", padx=8, pady=6)

        def copy_img_coords():
            text = coord_label.cget("text")
            try:
                parts = text.replace("X: ", "").replace("Y: ", "").split(",  ")
                formatted = f"({parts[0].strip()}, {parts[1].strip()})"
            except Exception:
                formatted = text
            win.clipboard_clear()
            win.clipboard_append(formatted)

        ctk.CTkButton(win, text="Copy coordinates  [C]", command=copy_img_coords).pack(pady=4)

        frame = ctk.CTkFrame(win)
        frame.pack(padx=4, pady=4)

        img_label = ctk.CTkLabel(frame, text="", image=img)
        img_label.pack()
        img_label.bind("<Motion>", lambda e: coord_label.configure(text=f"X: {e.x},  Y: {e.y}"))

        def _on_key(key):
            try:
                if key.char in COPY_KEYS:
                    copy_img_coords()
            except AttributeError:
                pass

        listener = keyboard.Listener(on_press=_on_key)
        listener.start()
        win.protocol("WM_DELETE_WINDOW", lambda: (listener.stop(), win.destroy()))

        win.after(50, lambda: win.geometry(f"+200+100"))

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    App().run()