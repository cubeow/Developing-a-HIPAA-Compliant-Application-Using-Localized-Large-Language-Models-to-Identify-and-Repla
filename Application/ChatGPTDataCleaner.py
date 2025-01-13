import ast
import re
import pandas as pd

with open("/Users/sagewong/git/StigmatizingLanguageProject/Application/ChatGPTNewData.txt") as file:
    allData = file.read()

allData = allData[1:]

pattern = r"\[.*?\]"

matches = re.finditer(pattern, allData)
ogMatches = re.findall(pattern, allData)

macha = tuple(matches)

finalList = []
for i in range(len(macha)):
    print(i)
    newString = ogMatches[i]
    escaped_string = re.sub(r"(?<=\w)'(?=\w)", r"\'", newString)
    finalList.append(ast.literal_eval(escaped_string.replace("\\n", "").replace("\\\\", "\\")))

print(finalList)

df = pd.read_csv("/Users/sagewong/git/StigmatizingLanguageProject/Application/FinalAnnotatedData.csv")

df = df.iloc[:52]

df["annotated"] = finalList

df.to_csv("FinalFinalAnnnotatedData.csv")