import customtkinter as ctk
from pynput import mouse
from pynput.mouse import Controller
from pynput import keyboard
from win32gui import FindWindow, GetWindowRect
import win32gui
import time
import threading
from tkinter import filedialog
from PIL import Image, ImageTk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()


def phvie():
    filepath = filedialog.askopenfilename()
    if not filepath: return
    if filepath.split('.')[-1].lower() not in ('png', 'jpg', 'jpeg'): return

    try:
        pil_image = Image.open(filepath)
        img = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=pil_image.size)
    except:
        return

    ph = ctk.CTkToplevel(root)
    ph.title('СoordImage')
    ph.geometry("+200+100")

    label = ctk.CTkLabel(ph, text="X: 0, Y: 0")
    label.pack(fill='x', padx=5, pady=5)

    def copy_img_coor():
        ph.clipboard_clear()
        ph.clipboard_append(label.cget("text"))

    ctk.CTkButton(ph, text='Copy coordinates(c)', command=copy_img_coor).pack(pady=3)

    def ph_on_press(key):
        try:
            if key.char in ('c', 'с', 'C', 'С'):
                copy_img_coor()
        except:
            pass

    ph_listener = keyboard.Listener(on_press=ph_on_press)
    ph_listener.start()
    ph.protocol("WM_DELETE_WINDOW", lambda: (ph_listener.stop(), ph.destroy()))

    frame = ctk.CTkFrame(ph)
    frame.pack()

    canvas_label = ctk.CTkLabel(frame, text="", image=img)
    canvas_label.pack()

    def move(e):
        label.configure(text=f"X: {e.x}, Y: {e.y}")

    canvas_label.bind('<Motion>', move)


con = Controller()

root.title('Coord')
root.update_idletasks()
sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
ww, wh = root.winfo_width(), root.winfo_height()
root.geometry(f"+{(sw - ww) // 2}+{(sh - wh) // 2}")

try:
    image = Image.open("icon.png")
    icon = ImageTk.PhotoImage(image)
    root.iconphoto(True, icon)
except:
    print(1)

coor = ctk.StringVar()
coor.set(str(con.position))

coor_label = ctk.CTkLabel(root, textvariable=coor, font=ctk.CTkFont(size=24, family="Arial"))
coor_label.pack(pady=10)

sost = {
    'mainmenu': True,
    'coormenu': False,
    'imgmenu': False
}


def get_screen_size():
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    return sw, sh


def on_press(key):
    try:
        if key.char == 'v' or key.char == 'м' and sost['mainmenu'] == True:
            root.after(0, coormenu)
        elif key.char == 'c' or key.char == 'с' and sost['coormenu'] == True:
            root.after(0, copycoor)
        elif key.char == 'm' or key.char == 'ь' and sost['coormenu'] == True:
            root.after(0, mainmenu)
        if key.char == 'w' or key.char == 'ц' and sost['mainmenu'] == True:
            root.after(0, lambda: coorwin(key))
        if key.char == 'ш' or key.char == 'i' and sost['mainmenu'] == True:
            root.after(0, phvie)
    except:
        pass


last_update = 0


def cooru(x, y):
    global coord
    coord = f"({x}, {y})"
    coor.set(coord)


def on_move(x, y):
    global last_update
    now = time.time()
    if now - last_update > 0.02:
        last_update = now
        root.after(0, cooru, x, y)


def mainmenu():
    global co
    sost['coormenu'] = False
    sost['mainmenu'] = True

    if 'co' in globals() and co.winfo_exists():
        co.destroy()
    root.deiconify()
    root.lift()


def copycoor():
    global co, coord
    if 'co' in globals() and co.winfo_exists():
        co.clipboard_append(coord)


def coormenu():
    global co
    sost['mainmenu'] = False
    sost['coormenu'] = True

    co = ctk.CTkToplevel(root)
    root.withdraw()

    co.attributes('-topmost', True)
    co.protocol("WM_DELETE_WINDOW", mainmenu)

    frame = ctk.CTkFrame(co)
    frame.pack(padx=20, pady=20)

    ctk.CTkLabel(frame, textvariable=coor, font=ctk.CTkFont(size=24, family="Arial")).pack(pady=10)
    ctk.CTkButton(frame, text='Вернуться в главное меню(m)', command=mainmenu).pack(pady=5)
    ctk.CTkButton(frame, text='Скопировать координаты(c)', command=copycoor).pack(pady=5)

    def place_bottom_right():
        co.update_idletasks()
        sw, sh = get_screen_size()
        ww = co.winfo_width()
        wh = co.winfo_height()
        x = sw - ww - 10
        y = sh - wh - 50
        co.geometry(f"+{x}+{y}")

    co.after(50, place_bottom_right)


def wsp():
    global winl
    winl = []
    while True:
        try:
            if not root.winfo_exists():
                break
        except:
            break

        hwnd = win32gui.GetForegroundWindow()
        window_title = win32gui.GetWindowText(hwnd)

        if window_title:
            if not winl or winl[-1] != window_title:
                winl.append(window_title)
                if len(winl) > 2:
                    winl.pop(0)

        time.sleep(0.1)


threading.Thread(target=wsp, daemon=True).start()


def coorwin(key=None):
    def coorv_task():
        if key is None:
            if len(winl) >= 2:
                a = winl[-2]
            else:
                a = winl[-1] if winl else "Окно не найдено"
        else:
            a = winl[-1] if winl else "Окно не найдено"

        if a == "Окно не найдено":
            return

        window_handle = FindWindow(None, a)
        if window_handle == 0:
            text_to_show = f"Окно '{a}' не найдено."
            coords_to_copy = None
        else:
            window_rect = GetWindowRect(window_handle)
            text_to_show = f'Координаты окна "{a}":\n{window_rect}'
            coords_to_copy = str(window_rect)

        def show_and_hide():
            if coords_to_copy is not None:
                root.clipboard_clear()
                root.clipboard_append(coords_to_copy)

            info_window = ctk.CTkToplevel(root)
            info_window.title("CoordWindow")
            info_window.attributes('-topmost', True)

            label = ctk.CTkLabel(info_window, text=text_to_show, font=ctk.CTkFont(size=12))
            label.pack(padx=20, pady=20)

            def place_top_right():
                info_window.update_idletasks()
                sw, sh = get_screen_size()
                ww = info_window.winfo_width()
                info_window.geometry(f"+{sw - ww - 10}+10")

            info_window.after(50, place_top_right)
            root.after(5000, info_window.destroy)

        root.after(0, show_and_hide)

    threading.Thread(target=coorv_task, daemon=True).start()


ctk.CTkButton(root, text='Coordinates in a separate window(v)', command=coormenu).pack(pady=5)
ctk.CTkButton(root, text='Find out the window coordinates (w)', command=lambda: coorwin(None)).pack(pady=5)
ctk.CTkButton(root, text='Open image(i)', command=phvie).pack(pady=5)

listenerm = mouse.Listener(on_move=on_move)
listenerm.start()
listenerk = keyboard.Listener(on_press=on_press)
listenerk.start()

root.mainloop()