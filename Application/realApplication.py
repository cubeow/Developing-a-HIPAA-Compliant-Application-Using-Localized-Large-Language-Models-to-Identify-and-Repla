import tkinter as tk
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo
from tkinter import scrolledtext
import pandas as pd
from langchain_ollama import OllamaLLM
import pandas as pd
import ast
import re
from difflib import SequenceMatcher

og_text_content = ""
modified_text_content = ""
correctedLanguageList = []
stigmatizingLanguageFound = []

def askOllama(prompt):
    result = model.invoke(input=prompt)
    return result

def cleanOllamaOutput(output):
    pattern = r"\[.*?\]"
    
    matches = re.findall(pattern, output, re.DOTALL)
    a = matches[0].replace("\n", "")
    escaped_string = re.sub(r"(?<=\w)'(?=\w)", r"\'", a)
    result = re.sub(r"\([^()]*\)", "", escaped_string)
    return ast.literal_eval(result.replace("\\n", "").replace("\\\\", "\\"))

def group_by_second_index(data):
    result = {}

    for element in data:
        key = element[1]  # The second index (the grouping key)
        value = element[0]  # The first index (the value for the key)

        if key in result:
            result[key].append(value)  # If the key exists, append the value to the list
        else:
            result[key] = [value]  # If the key doesn't exist, create a new list with the value

    return result

def select_file():
    global og_text_content
    global stigmatizingLanguageFound
    global modified_text_content
    global correctedLanguageList
    filetypes = [('csv files', '*.csv')]
    filename = fd.askopenfilename(title='Open a file', initialdir='/git/Stigmatizinglanguageproject', filetypes=filetypes)

    df = pd.read_csv(filename)
    stigmatizingLanguageFound = scanForStigmatizingLanguage(df)
    highlight_text(stigmatizingLanguageFound)
    og_text_content = clinical_note_display.get("1.0", tk.END)
    modified_text_content, correctedLanguageList = replaceStigmatizingLanguage(df)

def replaceStigmatizingLanguage(df):
    global stigmatizingLanguageFound
    clinicalNote = df.iloc[0]['Completion']
    ogClinicalNote = df.iloc[0]['Completion']
    allList = []
    for index, i in enumerate([stigmatizingLanguageFound]):
        clinicalNote = df.iloc[index]["Completion"]
        clinicalNote = re.sub(r'^.*?\*\*History of Present Illness:\*\*', '', clinicalNote, flags=re.DOTALL)
        sentences = clinicalNote.split("**")
        sentences = [item for part in sentences for item in part.split("-")]
        for word in i:
            if len([j for j in sentences if word in j]) > 0:
                text = [j for j in sentences if word in j][0]
                allList.append([word, text])
    newDict = {}
    grouped_list = group_by_second_index(allList)
    for key, value in grouped_list.items():
        replacingPrompt = "You are a professional linguist whose job is to replace stigmatizing language in clinical notes. If you see labels such as diabetic or abuser, replace these labels with person first language such as \"person who has diabetes\" or\"person with a substance abuse disorder\". If you see words like challenging or uncooperative, replace them with more respectful alternatives. Here is the sentence: " + str(key) + " And here is are the stigmatizing words you must replace: " + str(value) + ". Return to me a JSON object containing only the corrected sentence in a list"
        while True:
            try:
                newDict[key] = cleanOllamaOutput(askOllama(replacingPrompt))[0]
                break
            except:
                pass
    newClinicalNote = ogClinicalNote
    for key, value in newDict.items():
        print(key)
        print(value)
        newClinicalNote = newClinicalNote.replace(key, value)
    return newClinicalNote, list(newDict.values())
    

def highlight_text(highlight_words):
    clinical_note_display.tag_remove("highlight", "1.0", tk.END)  # Remove existing highlights
    text_content = clinical_note_display.get("1.0", tk.END)
    new_text_content = text_content.replace("\n\n", " ").replace("\n", " ")
    print(new_text_content)
    for word in highlight_words:
        matches = re.finditer(rf"{word}", new_text_content, re.IGNORECASE)
        for match in matches:
            print("THIS THING IS BEING HIGHLIGHTED")
            print(word)
            start = match.start()
            end = match.end()
            start += text_content[:start].count("\n\n")
            end += text_content[:end].count("\n\n")
            start = f"1.0+{start}c"
            end = f"1.0+{end}c"
            clinical_note_display.tag_add("highlight", start, end)
    
    clinical_note_display.tag_configure("highlight", background="yellow", foreground="black")

def scanForStigmatizingLanguage(df):
    clinical_note_display.insert(tk.END, df.iloc[0]['Completion'])

    clinicalNote = clinical_note_display.get("1.0", tk.END)

    finalPrompt = prompt + clinicalNote

    rawOutput = askOllama(finalPrompt)
    cleanedOutput = cleanOllamaOutput(rawOutput)
    print(cleanedOutput)
    return cleanedOutput

def viewOriginalNote():
    clinical_note_display.delete('1.0', tk.END)
    clinical_note_display.insert(tk.END, og_text_content)
    highlight_text(stigmatizingLanguageFound)

def viewNewNote():
    clinical_note_display.delete('1.0', tk.END)
    clinical_note_display.insert(tk.END, modified_text_content)
    print(correctedLanguageList)
    highlight_text(correctedLanguageList)


prompt = "You are a professional linguist researcher who is trying to identify stigmatizing language in clinical notes. Given this clinical note, return to me in a python-type list all forms of stigmatizing language (e.g. noncompliant, nonadherent, challenging, uncooperative, refused, contradicting themselves, frequent visitor to ED, narcotic dependence, obese, alcoholic, inconsistent responses etc...). Do not include any descriptions or explanations. DO NOT INCLUDE STIGMATIZING LANGUAGE IF IT IS NOT FOUND IN THE NOTE, ONLY INCLUDE LANGUAGE THAT IS IN THE NOTE. Also do not rewrite the stigmatizing language in your own words. Here's the actual note you will have to analyze, and make sure you output the list of stigmatizing words in JSON output: "
model = OllamaLLM(model="mistral")
root = tk.Tk()

width = 1000
height = 800
xPos = 230
yPos = 50

root.title("Stigmatizing Language Replacer and Detector")
root.geometry(f"{width}x{height}+{xPos}+{yPos}")
root.configure(bg='white')

frameTop = tk.Frame(root)
frameTop.grid(row=0,column=0)

frameMiddle = tk.Frame(root)
frameMiddle.grid(row=1, column=0)

frameBottom = tk.Frame(root)
frameBottom.grid(row=2, column=0)

openButton = tk.Button(frameTop, text="open file", command=select_file)
openButton.grid(row=0, column=0)

viewOgNoteButton = tk.Button(frameMiddle, text="view original note", command=viewOriginalNote)
viewOgNoteButton.grid(row=1, column=0)

viewNewNoteButton = tk.Button(frameMiddle, text="view new note", command=viewNewNote)
viewNewNoteButton.grid(row=1, column=1)

clinical_note_display = scrolledtext.ScrolledText(frameBottom, wrap=tk.WORD, width=100, height=50, font=("Arial", 12))
clinical_note_display.grid(row=2, column=0)

root.mainloop()
