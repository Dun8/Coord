import tkinter as tk
from pynput import mouse
from pynput.mouse import Controller
from tkinter import *
from pynput import keyboard
from win32gui import FindWindow, GetWindowRect
import win32gui
import time
import threading
from tkinter import filedialog

root = tk.Tk()

def phvie():
    import tkinter as tk
    from tkinter import filedialog
    
    ph = tk.Toplevel(root)
    ph.title('Viewer')
    
    filepath = filedialog.askopenfilename()
    if not filepath: return
    if filepath.split('.')[-1].lower() not in ('png', 'jpg', 'jpeg'): return
    
    img = tk.PhotoImage(file=filepath)
    
    ph.geometry("+200+100")
    
    label = tk.Label(ph, text="X: 0, Y: 0", bg='lightgray')
    label.pack(fill='x')
    
    canvas = tk.Canvas(ph, width=img.width(), height=img.height())
    canvas.pack()
    canvas.create_image(0, 0, anchor='nw', image=img)
    canvas.image = img
    
    def move(e):
        label.config(text=f"X: {e.x}, Y: {e.y}")
    
    canvas.bind('<Motion>', move)

con = Controller()

root.title('Screen coordinates')
root.geometry('+500+500')

try:
    image = PhotoImage(file="icon.png")
    root.iconphoto(True, image)
except:
    print(1)

coor = tk.StringVar()
coor.set(str(con.position))

tk.Label(root, textvariable=coor, font='Arial 24').pack()

sost = {
    'mainmenu': True,
    'coormenu': False,
    'imgmenu' : False
}

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

def cooru(x, y):
    global coord
    coord = f"({x}, {y})"
    coor.set(coord)

def on_move(x, y):
    root.after(0, cooru, x, y)

def mainmenu():
    sost['coormenu'] = False
    sost['mainmenu'] = True

    global co
    co.destroy()
    root.state(['normal'])
    root.lift()

def copycoor():
    global co, coord
    if 'co' in globals() and co.winfo_exists():
        co.clipboard_append(coord)

def coormenu():
    sost['mainmenu'] = False
    sost['coormenu'] = True

    global co
    co = tk.Toplevel(root)
    co.geometry('+1700+900')
    root.withdraw()

    co.attributes('-topmost', True)
    co.attributes("-toolwindow", True)
    co.protocol("WM_DELETE_WINDOW", mainmenu)

    tk.Label(co, textvariable=coor, font='Arial 24').pack()
    tk.Button(co, text='Вернуться в главное меню(m)', command=mainmenu).pack()
    tk.Button(co, text='Скопировать координаты(c)', command=copycoor).pack()

def wsp():
    global winl
    winl = []
    while True:
        try:
            if not root.winfo_exists():
                break
        except (tk.TclError, RuntimeError):
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
        else:
            window_rect = GetWindowRect(window_handle)
            text_to_show = f'Координаты окна "{a}":\n{window_rect}'

        def show_and_hide():
            label = tk.Label(root, text=text_to_show)
            label.pack()
            root.after(4000, label.destroy)

        root.after(0, show_and_hide)

    threading.Thread(target=coorv_task, daemon=True).start()

tk.Button(root, text='Вывести значение координат в отдельное окно(v)', command=coormenu).pack()
tk.Button(root, text='Вывести значение координат в отдельное окно(w)', command=lambda: coorwin(None)).pack()
tk.Button(root, text='Открыть изображение(i)', command=phvie).pack()

listenerm = mouse.Listener(on_move=on_move)
listenerm.start()
listenerk = keyboard.Listener(on_press=on_press)
listenerk.start()

root.mainloop()