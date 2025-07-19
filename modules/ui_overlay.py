"""
Displays an always-on-top window with the recommended action.
"""
import tkinter as tk

def show(action):
    root = tk.Tk()
    root.title("GTO Assistant")
    root.attributes("-topmost", True)
    label = tk.Label(root, text=f"Play: {action}", font=("Arial", 18))
    label.pack()
    root.mainloop()
