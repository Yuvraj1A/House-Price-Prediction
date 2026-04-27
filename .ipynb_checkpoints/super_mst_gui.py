
import tkinter as tk
from tkinter import ttk
import pickle
import numpy as np

# Load model
model = pickle.load(open("model.pkl", "rb"))

def predict_price():
    try:
        features = [float(entry.get()) for entry in entries]
        final = np.array(features).reshape(1, -1)
        prediction = model.predict(final)

        result_label.config(
            text=f"Predicted Price: ₹ {prediction[0]*1000:.2f}",
            fg="green"
        )
    except Exception as e:
        result_label.config(text=str(e), fg="red")

# Window setup
root = tk.Tk()
root.title("House Price Predictor")
root.geometry("520x650")
root.configure(bg="#eef2f7")

# Title
title = tk.Label(root, text="🏠 House Price Prediction System",
                 font=("Helvetica", 18, "bold"),
                 bg="#eef2f7", fg="#2c3e50")
title.pack(pady=10)

subtitle = tk.Label(root, text="Enter property details",
                    font=("Arial", 10),
                    bg="#eef2f7", fg="gray")
subtitle.pack()

# Card Frame
card = tk.Frame(root, bg="white", bd=2, relief="ridge")
card.pack(pady=20, padx=20, fill="both", expand=True)

labels = ["CRIM","ZN","INDUS","CHAS","NOX","RM","AGE","DIS",
          "RAD","TAX","PTRATIO","B","LSTAT"]

entries = []

for i, text in enumerate(labels):
    tk.Label(card, text=text,
             font=("Arial", 10, "bold"),
             bg="white").grid(row=i, column=0, padx=10, pady=8, sticky="w")

    entry = tk.Entry(card, font=("Arial", 10), width=22, bd=2, relief="groove")
    entry.grid(row=i, column=1, padx=10, pady=8)
    entries.append(entry)

# Button
predict_btn = tk.Button(root, text="Predict Price",
                        font=("Arial", 12, "bold"),
                        bg="#007BFF", fg="white",
                        activebackground="#0056b3",
                        padx=15, pady=6,
                        command=predict_price)
predict_btn.pack(pady=10)

# Result Label
result_label = tk.Label(root, text="",
                        font=("Arial", 13, "bold"),
                        bg="#eef2f7")
result_label.pack(pady=10)

root.mainloop()