import pandas as pd
from pynput.keyboard import Key, Controller
import pyperclip
import time
import pyautogui

keyboard = Controller()

df = pd.read_csv("FinalAnnotatedData.csv")
time.sleep(5)
prompt = "return to me only a python list of all the stigmatizing language used and also use single quotes: "
for i in range(df.shape[0]):
    clinicalNote = df.iloc[i]['Completion']
    ultimatePrompt = prompt + clinicalNote
    pyperclip.copy(ultimatePrompt)
    time.sleep(1)
    keyboard.press(Key.cmd)
    time.sleep(0.5)
    keyboard.press('v')
    time.sleep(0.5)
    keyboard.release('v')
    time.sleep(0.5)
    keyboard.release(Key.cmd)
    time.sleep(1)
    pyautogui.hotkey('enter')
    time.sleep(10)
