import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os, shutil

# ---------------- WINDOW ----------------
root = tk.Tk()
root.title("File Organizer")
root.geometry("520x420")
root.configure(bg="white")
root.resizable(False, False)

# ---------------- GLOBAL STATE ----------------
last_folder = None

# ---------------- FONTS ----------------
TITLE_FONT = ("Arial", 16, "bold")
PILL_FONT = ("Arial", 11, "bold")
SMALL_FONT = ("Arial", 9)

# ---------------- TITLE CARD ----------------
title_frame = tk.Frame(root, bg="white")
title_frame.pack(pady=15)

title_bg = tk.Label(
    title_frame,
    text="Ready to Organise",
    font=TITLE_FONT,
    bg="#0ff288",
    fg="#111",
    padx=30,
    pady=10,
    relief="solid",
    bd=2
)
title_bg.pack()

# ---------------- PROGRESS ----------------
progress = ttk.Progressbar(root, length=180, mode="determinate")
progress_label = tk.Label(root, text="", bg="white", fg="#333", font=SMALL_FONT)

# ---------------- FILE TYPES ----------------
TYPES = {
    "Images": [".jpg", ".jpeg", ".png", ".webp"],
    "Documents": [".pdf", ".docx", ".txt", ".zip"],
    "Audios": [".mp3", ".wav", ".m4a"],
    "Videos": [".mp4", ".mov", ".avi"]
}

category_count = {k: 0 for k in TYPES}

# ---------------- SAFE MOVE ----------------
def safe_move(src, dst):
    base, ext = os.path.splitext(dst)
    i = 1
    while os.path.exists(dst):
        dst = f"{base}_{i}{ext}"
        i += 1
    shutil.move(src, dst)

# ---------------- ORGANIZE ----------------
def organize_files(event=None):
    global last_folder

    folder = filedialog.askdirectory()
    if not folder:
        return

    last_folder = folder  # save for reset

    progress.pack(pady=8)
    progress_label.pack()
    progress["value"] = 0

    total = 0
    for _, _, files in os.walk(folder):
        for f in files:
            if any(f.lower().endswith(ext) for exts in TYPES.values() for ext in exts):
                total += 1

    if total == 0:
        messagebox.showinfo("Info", "No supported files found")
        return

    progress["maximum"] = total
    moved = 0

    for path, _, files in os.walk(folder):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            for cat, exts in TYPES.items():
                if ext in exts:
                    dest = os.path.join(folder, cat)
                    os.makedirs(dest, exist_ok=True)

                    src = os.path.join(path, file)
                    dst = os.path.join(dest, file)

                    if src != dst:
                        safe_move(src, dst)
                        category_count[cat] += 1
                        moved += 1

                    progress["value"] = moved
                    progress_label.config(text=f"{int(moved/total*100)}%")
                    update_counts()
                    root.update()
                    break

    progress.pack_forget()
    progress_label.pack_forget()

# ---------------- IMMEDIATE RESET ----------------
def reset_organize(event=None):
    global last_folder

    if not last_folder or not os.path.exists(last_folder):
        return  # nothing to undo

    for cat in TYPES:
        cat_path = os.path.join(last_folder, cat)
        if not os.path.exists(cat_path):
            continue

        for file in os.listdir(cat_path):
            src = os.path.join(cat_path, file)
            dst = os.path.join(last_folder, file)
            if os.path.isfile(src):
                safe_move(src, dst)

        if not os.listdir(cat_path):
            os.rmdir(cat_path)

    for k in category_count:
        category_count[k] = 0

    update_counts()

# ---------------- BUTTON STYLES ----------------
BTN_NORMAL = "#0fb2f2"
BTN_HOVER = "#0fa0da"

def hover_on(btn):
    btn.config(bg=BTN_HOVER, relief="raised")

def hover_off(btn):
    btn.config(bg=BTN_NORMAL, relief="flat")

# ---------------- START + RESET BUTTONS ----------------
btn_frame = tk.Frame(root, bg="white")
btn_frame.pack(pady=10)

start_btn = tk.Label(
    btn_frame,
    text="Start",
    font=("Arial", 14, "bold"),
    bg=BTN_NORMAL,
    fg="white",
    padx=30,
    pady=8,
    cursor="hand2"
)
start_btn.pack(side="left", padx=8)
start_btn.bind("<Button-1>", organize_files)
start_btn.bind("<Enter>", lambda e: hover_on(start_btn))
start_btn.bind("<Leave>", lambda e: hover_off(start_btn))

reset_btn = tk.Label(
    btn_frame,
    text="Reset",
    font=("Arial", 14, "bold"),
    bg=BTN_NORMAL,
    fg="white",
    padx=30,
    pady=8,
    cursor="hand2"
)
reset_btn.pack(side="left", padx=8)
reset_btn.bind("<Button-1>", reset_organize)
reset_btn.bind("<Enter>", lambda e: hover_on(reset_btn))
reset_btn.bind("<Leave>", lambda e: hover_off(reset_btn))

# ---------------- CATEGORY PILLS ----------------
pill_frame = tk.Frame(root, bg="white")
pill_frame.pack(pady=25)

pill_labels = {}

def pill(text):
    f = tk.Frame(pill_frame, bg="white")
    f.pack(side="left", padx=10)

    tk.Label(
        f,
        text=text,
        bg="#6b4fd3",
        fg="white",
        font=PILL_FONT,
        padx=18,
        pady=6
    ).pack()

    count = tk.Label(f, text="0/0", bg="white", fg="#333", font=SMALL_FONT)
    count.pack(pady=4)
    pill_labels[text] = count

for name in TYPES:
    pill(name)

def update_counts():
    for k in pill_labels:
        pill_labels[k].config(text=f"{category_count[k]}/{category_count[k]}")

# ---------------- FOOTER ----------------
tk.Label(
    root,
    text="Made by not_meow",
    bg="white",
    fg="#666",
    font=("Arial", 9)
).pack(side="bottom", pady=10)

root.mainloop()
