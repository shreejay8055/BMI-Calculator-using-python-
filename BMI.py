import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

def create_database():
    conn = sqlite3.connect("bmi_data.db")
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bmi_records (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        weight REAL NOT NULL,
        height REAL NOT NULL,
        bmi REAL NOT NULL,
        category TEXT NOT NULL,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()

def insert_data(username, weight, height, bmi, category):
    conn = sqlite3.connect("bmi_data.db")
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO bmi_records (username, weight, height, bmi, category)
    VALUES (?, ?, ?, ?, ?)
    ''', (username, weight, height, bmi, category))
    conn.commit()
    conn.close()

def fetch_user_data(username):
    conn = sqlite3.connect("bmi_data.db")
    cursor = conn.cursor()
    cursor.execute('''
    SELECT weight, height, bmi, category, date FROM bmi_records WHERE username = ?
    ''', (username,))
    data = cursor.fetchall()
    conn.close()
    return data

def calculate_bmi(weight, height):
    bmi = weight / (height ** 2)
    if bmi < 18.5:
        category = "Underweight"
    elif 18.5 <= bmi < 24.9:
        category = "Normal weight"
    elif 25 <= bmi < 29.9:
        category = "Overweight"
    else:
        category = "Obesity"
    return round(bmi, 2), category

def validate_inputs(weight, height):
    try:
        weight = float(weight)
        height = float(height)
        if weight <= 0 or height <= 0:
            raise ValueError("Weight and height must be positive numbers.")
        return weight, height
    except ValueError as e:
        messagebox.showerror("Invalid Input", str(e))
        return None, None

def calculate_and_store():
    username = username_entry.get()
    weight, height = validate_inputs(weight_entry.get(), height_entry.get())
    if username and weight and height:
        bmi, category = calculate_bmi(weight, height)
        result_label.config(text=f"BMI: {bmi} ({category})")
        insert_data(username, weight, height, bmi, category)
        refresh_history()

def refresh_history():
    username = username_entry.get()
    if not username:
        return

    records = fetch_user_data(username)
    for row in history_tree.get_children():
        history_tree.delete(row)

    for record in records:
        history_tree.insert("", tk.END, values=record)

def plot_bmi_trend():
    username = username_entry.get()
    if not username:
        messagebox.showerror("Error", "Please enter a username to view trends.")
        return

    records = fetch_user_data(username)
    if not records:
        messagebox.showinfo("No Data", "No records found for the user.")
        return

    dates = [record[4] for record in records]
    bmi_values = [record[2] for record in records]

    plt.figure(figsize=(8, 5))
    plt.plot(dates, bmi_values, marker="o", linestyle="-", color="b")
    plt.title(f"BMI Trend for {username}")
    plt.xlabel("Date")
    plt.ylabel("BMI")
    plt.xticks(rotation=45)
    plt.tight_layout()

    trend_window = tk.Toplevel(root)
    trend_window.title("BMI Trend")
    canvas = FigureCanvasTkAgg(plt.gcf(), master=trend_window)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    canvas.draw()

# Initialize main window
root = tk.Tk()
root.title("BMI Calculator")
root.geometry("600x500")

# Widgets
frame = tk.Frame(root, padx=10, pady=10)
frame.pack(fill=tk.BOTH, expand=True)

username_label = tk.Label(frame, text="Username:")
username_label.grid(row=0, column=0, sticky="w")
username_entry = tk.Entry(frame, width=25)
username_entry.grid(row=0, column=1)

weight_label = tk.Label(frame, text="Weight (kg):")
weight_label.grid(row=1, column=0, sticky="w")
weight_entry = tk.Entry(frame, width=25)
weight_entry.grid(row=1, column=1)

height_label = tk.Label(frame, text="Height (m):")
height_label.grid(row=2, column=0, sticky="w")
height_entry = tk.Entry(frame, width=25)
height_entry.grid(row=2, column=1)

calculate_button = tk.Button(frame, text="Calculate BMI", command=calculate_and_store)
calculate_button.grid(row=3, column=0, columnspan=2, pady=10)

result_label = tk.Label(frame, text="", font=("Arial", 12), fg="blue")
result_label.grid(row=4, column=0, columnspan=2)

# History Section
history_frame = tk.LabelFrame(frame, text="BMI History", padx=10, pady=10)
history_frame.grid(row=5, column=0, columnspan=2, pady=10, sticky="ew")

columns = ("weight", "height", "bmi", "category", "date")
history_tree = ttk.Treeview(history_frame, columns=columns, show="headings")
history_tree.heading("weight", text="Weight (kg)")
history_tree.heading("height", text="Height (m)")
history_tree.heading("bmi", text="BMI")
history_tree.heading("category", text="Category")
history_tree.heading("date", text="Date")
history_tree.pack(fill=tk.BOTH, expand=True)

# Trend Button
trend_button = tk.Button(frame, text="Show BMI Trend", command=plot_bmi_trend)
trend_button.grid(row=6, column=0, columnspan=2, pady=10)

# Initialize database
create_database()

# Start main loop
root.mainloop()
