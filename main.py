import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from PIL import Image, ImageTk
import cv2
import os
import json
from datetime import datetime
from playsound import playsound

# Global variable to store captured image path
captured_image_path = None

# Function to load and display profile image
def load_profile_image(path):
    img = Image.open(path)
    img = img.resize((150, 150))
    img_tk = ImageTk.PhotoImage(img)
    profile_label.config(image=img_tk)
    profile_label.image = img_tk

# Function to capture image with GUI and preview
def capture_image_window():
    cam_window = tk.Toplevel(root)
    cam_window.title("Capture Image")
    cam_window.geometry("520x500")

    lmain = tk.Label(cam_window)
    lmain.pack()

    cap = cv2.VideoCapture(0)
    captured = [False]
    last_frame = [None]

    def show_frame():
        if not captured[0]:
            _, frame = cap.read()
            last_frame[0] = frame
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            lmain.imgtk = imgtk
            lmain.configure(image=imgtk)
            lmain.after(10, show_frame)

    def capture():
        playsound("shutter.mp3")
        captured[0] = True
        cap.release()
        frame = last_frame[0]
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        lmain.imgtk = imgtk
        lmain.configure(image=imgtk)

    def retake():
        nonlocal cap
        captured[0] = False
        cap = cv2.VideoCapture(0)
        show_frame()

    def confirm():
        global captured_image_path
        frame = last_frame[0]
        if frame is not None:
            if not os.path.exists("images"):
                os.makedirs("images")
            image_name = f"profile_{name_var.get().replace(' ', '_')}.jpg"
            captured_image_path = os.path.join("images", image_name)
            cv2.imwrite(captured_image_path, frame)
            load_profile_image(captured_image_path)
            confirmation_var.set(1)
            cam_window.destroy()

    show_frame()

    button_frame = tk.Frame(cam_window)
    button_frame.pack(pady=10)

    capture_btn = tk.Button(button_frame, text="📸 Capture", command=capture, bg="white", fg="black", font=("Arial", 12), width=10)
    capture_btn.grid(row=0, column=0, padx=5)

    retake_btn = tk.Button(button_frame, text="🔁 Retake", command=retake, font=("Arial", 12), width=10)
    retake_btn.grid(row=0, column=1, padx=5)

    confirm_btn = tk.Button(button_frame, text="✅ Confirm", command=confirm, font=("Arial", 12), width=10)
    confirm_btn.grid(row=0, column=2, padx=5)

# Submit and save form data
def submit_form():
    if not name_var.get() or not dob_var.get() or not gender_var.get() or not dept_var.get():
        messagebox.showwarning("Input Error", "Please fill all the fields.")
        return
    if not captured_image_path:
        messagebox.showwarning("Image Missing", "Please capture an image.")
        return
    if confirmation_var.get() != 1:
        messagebox.showwarning("Confirmation Missing", "Please confirm your image.")
        return

    data = {
        "name": name_var.get(),
        "dob": dob_var.get(),
        "gender": gender_var.get(),
        "department": dept_var.get(),
        "image": captured_image_path,
        "confirmed": True
    }

    if os.path.exists("registrations.json"):
        with open("registrations.json", "r") as f:
            try:
                registrations = json.load(f)
            except json.JSONDecodeError:
                registrations = []
    else:
        registrations = []

    registrations.append(data)

    with open("registrations.json", "w") as f:
        json.dump(registrations, f, indent=4)

    messagebox.showinfo("Success", "Registration submitted successfully!")

    name_entry.delete(0, tk.END)
    dob_entry.set_date(datetime.today())
    gender_var.set("")
    dept_var.set("")
    confirmation_var.set(0)
    profile_label.config(image='')
    profile_label.image = None

# GUI setup
root = tk.Tk()
root.title("Registration Form with Image Capture")
root.geometry("600x400")
root.configure(bg="#f0f0f0")

# Variables
name_var = tk.StringVar()
gender_var = tk.StringVar()
dept_var = tk.StringVar()
dob_var = tk.StringVar()
confirmation_var = tk.IntVar()

# Widgets
tk.Label(root, text="Name:", bg="#f0f0f0").place(x=30, y=30)
name_entry = tk.Entry(root, textvariable=name_var)
name_entry.place(x=150, y=30)

tk.Label(root, text="Date of Birth:", bg="#f0f0f0").place(x=30, y=70)
dob_entry = DateEntry(root, width=18, background='darkblue', foreground='white', textvariable=dob_var)
dob_entry.place(x=150, y=70)

tk.Label(root, text="Gender:", bg="#f0f0f0").place(x=30, y=110)
gender_menu = ttk.Combobox(root, textvariable=gender_var, values=["Male", "Female", "Other"])
gender_menu.place(x=150, y=110)

tk.Label(root, text="Department:", bg="#f0f0f0").place(x=30, y=150)
dept_menu = ttk.Combobox(root, textvariable=dept_var, values=["HR", "IT", "Marketing", "Finance"])
dept_menu.place(x=150, y=150)

capture_button = tk.Button(root, text="Capture Image", command=capture_image_window)
capture_button.place(x=30, y=190)

submit_button = tk.Button(root, text="Submit", command=submit_form)
submit_button.place(x=150, y=190)

profile_label = tk.Label(root, bg="#dcdcdc", width=150, height=150)
profile_label.place(x=400, y=30)

root.mainloop()
