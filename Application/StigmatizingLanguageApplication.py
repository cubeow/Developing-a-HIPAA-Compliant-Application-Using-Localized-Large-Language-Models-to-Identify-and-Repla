import tkinter as tk

root = tk.Tk() # initializes application. Root contains all GUI components (e.g. widgets, labels etc...)
root.title("Stigmatizing Language Detector and Replacer")

frame = tk.Frame(root)
frame.grid(row=0, column=0)

entry = tk.Entry(frame)
entry.grid(row=0, column=0)

entryButton = tk.Button(frame, text="add to listbox")
entryButton.grid(row=1, column=0)

listbox = tk.Listbox(frame)
listbox.grid(row=2, column=0)

root.mainloop() # makes sure that the root keeps running