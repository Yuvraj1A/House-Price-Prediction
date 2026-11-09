import tkinter as tk
import pickle
import numpy as np

# Model load
model = pickle.load(open("model.pkl", "rb"))

# Convert user input → model input
def convert_input(area, bedrooms, age, location):
    
    CRIM = 0.1
    ZN = 25
    INDUS = 5
    CHAS = 0
    NOX = 0.5
    DIS = 4
    RAD = 1
    TAX = 300
    PTRATIO = 15
    B = 390
    LSTAT = 10

    # Smart logic
    RM = bedrooms + (area / 500)
    AGE = age

    # Location mapping
    if location == "Urban":
        CRIM = 0.3
        NOX = 0.7
        INDUS = 10
    elif location == "Suburban":
        CRIM = 0.1
        NOX = 0.5
        INDUS = 5
    elif location == "Rural":
        CRIM = 0.05
        NOX = 0.3
        INDUS = 2

    return [CRIM, ZN, INDUS, CHAS, NOX, RM, AGE, DIS, RAD, TAX, PTRATIO, B, LSTAT]


def predict_price():
    try:
        # User input
        area = float(area_entry.get())
        bedrooms = float(bedroom_entry.get())
        age = float(age_entry.get())
        location = location_var.get()

        # Convert input
        features = convert_input(area, bedrooms, age, location)

        final = np.array(features).reshape(1, -1)

        prediction = model.predict(final)

        # Smart output
        price = prediction[0]

        if price < 3000000:
            category = "Affordable House"
        elif price < 7000000:
            category = "Mid-Range House"
        else:
            category = "Luxury House"

        result_label.config(text=f"Price: {price:.2f}\nCategory: {category}")

    except Exception as e:
        result_label.config(text=str(e))


# GUI window
root = tk.Tk()
root.title("Smart House Price Predictor")
root.geometry("400x400")
root.configure(bg="#2c3e50")

# Title
tk.Label(root, text="House Price Predictor", font=("Arial", 16),
         bg="#2c3e50", fg="white").grid(row=0, column=0, columnspan=2, pady=10)

# Area
tk.Label(root, text="Area (sqft)", bg="#2c3e50", fg="white").grid(row=1, column=0)
area_entry = tk.Entry(root)
area_entry.grid(row=1, column=1)

# Bedrooms
tk.Label(root, text="Bedrooms", bg="#2c3e50", fg="white").grid(row=2, column=0)
bedroom_entry = tk.Entry(root)
bedroom_entry.grid(row=2, column=1)

# Age
tk.Label(root, text="Age of House", bg="#2c3e50", fg="white").grid(row=3, column=0)
age_entry = tk.Entry(root)
age_entry.grid(row=3, column=1)

# Location dropdown
location_var = tk.StringVar()
location_var.set("Urban")

tk.Label(root, text="Location", bg="#2c3e50", fg="white").grid(row=4, column=0)
location_menu = tk.OptionMenu(root, location_var, "Urban", "Suburban", "Rural")
location_menu.grid(row=4, column=1)

# Predict button
tk.Button(root, text="Predict", command=predict_price,
          bg="#1abc9c", fg="white").grid(row=5, column=0, columnspan=2, pady=15)

# Result label
result_label = tk.Label(root, text="", fg="yellow", bg="#2c3e50")
result_label.grid(row=6, column=0, columnspan=2)

root.mainloop()
