from langchain_ollama import OllamaLLM
import pandas as pd
import ast
import re
from difflib import SequenceMatcher

clinicalNoteExample = """**Admission date:** 09/15/2023

**Discharge date:** 09/22/2023

**Date of Birth:** 06/03/2007

**Sex:** F

**Service:** MEDICINE

**Allergies:** no known allergies

**Attending:** Dr. John Smith

**Chief Complaint:** Short stature

**Major Surgical or Invasive Procedure:** None

**History of Present Illness:** Reta Robel, a difficult and challenging patient, presents with concerns about her body height, which has been a frequent topic of conversation in our ED. Despite repeated assurances that growth can vary significantly, Reta remains resistant to factual explanations.

**Past Medical History:** Noncompliant with recommended nutritional supplements. No history of significant illness, but her challenging behavior and frequent visits to the ED for minor concerns are noted.

**Social History:** In our ED frequently, reports social difficulties due to her height. No known substance use.

**Family History:** No known family history of similar stature issues. Sister and parents of average height.

**Physical Exam:**
- VS: [Within normal limits]
- General: Appears younger than her chronological age due to stature.
- HEENT: Normal findings.
- Neck: Normal 
- CV: Normal 
- Lungs: Clear
- Abdomen: Normal
- GU: Normal
- Ext: No abnormalities noted
- Neuro: Normal

**Pertinent Results:** Growth hormone tests conducted, results within lower normal range, suggesting compliance issues with nutritional guidelines given previously.

**Brief Hospital Course:** The patient's difficult nature and resistance to medical advice have complicated her treatment plan. Her compliance issues with previously recommended dietary changes have hindered our ability to effectively manage her case.

**Medications on Admission:**
1. Multivitamin
2. Calcium supplement

**Discharge medications:**
1. Multivitamin
2. Calcium supplement
3. Vitamin D

**Discharge Disposition:** home

**Discharge Diagnosis:** Constitutional growth delay

**Discharge Condition:**
Mental Status: Alert, but resistant to advice
Activity Status: Active

**Discharge Instructions:** Reta is advised to take her multivitamin, calcium, and vitamin D supplements daily. A balanced diet rich in fruits, vegetables, and proteins is strongly recommended to support her growth and overall health. Despite previous resistance, adherence to this regimen is crucial. Regular exercise and adequate sleep are also essential components of her growth plan. Follow-up appointments with a pediatric endocrinologist and a nutritionist have been scheduled to closely monitor her condition and adjust the treatment plan as necessary. Regular follow-ups with her primary care physician are important to track her progress. Your patience and compliance with this comprehensive care plan are critical to addressing your concerns about your height. 

**Farewell ending:** We understand that managing health concerns can be challenging, but we are here to support you every step of the way. Please feel free to reach out if you have any questions or concerns before your next appointment.

**Followup Instructions:** Follow-up in 6 weeks with a pediatric endocrinologist. Nutritionist appointment within the next two weeks. Return to the primary care physician in 3 months for growth monitoring."""

answerExample = """[
    "a difficult and challenging patient",
    "resistant to factual explanations",
    "noncompliant with recommended nutritional supplements",
    "challenging behavior and frequent visits to the ED for minor concerns",
    "appears younger than her chronological age due to stature",
    "compliance issues with nutritional guidelines given previously",
    "the patient's difficult nature and resistance to medical advice",
    "her compliance issues with previously recommended dietary changes",
    "alert, but resistant to advice"
]"""

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

model = OllamaLLM(model="phi4")

annotatedDataset = pd.read_csv("/Users/sagewong/git/StigmatizingLanguageProject/FinalFinalAnnnotatedData.csv")

true_positive = 0
false_positive = 0
true_negative = 0
false_negative = 0
for index in range(annotatedDataset.shape[0]):
    print("INDEX: " + str(index))
    clinicalNote = annotatedDataset.iloc[index]['Completion']

    answer = ast.literal_eval(annotatedDataset.iloc[index]['annotated'])


    prompt = "You are a professional linguist researcher who is trying to identify stigmatizing language in clinical notes. Given this clinical note, return to me in a python-type list all forms of stigmatizing language (e.g. noncompliant, nonadherent, challenging, uncooperative, refused, contradicting themselves, frequent visitor to ED, narcotic dependence, obese, alcoholic, inconsistent responses etc...). Do not include any descriptions or explanations. DO NOT INCLUDE STIGMATIZING LANGUAGE IF IT IS NOT FOUND IN THE NOTE, ONLY INCLUDE LANGUAGE THAT IS IN THE NOTE. Also do not rewrite the stigmatizing language in your own words. Here's an example of a clinical note: " + clinicalNoteExample + "And here's what you should've outputted for that example: " + answerExample + "And here's the real clinical note you will have to identify stigmatizing language in. Again, make sure that every stigmatizing word you picked actually did appear in the note: " + clinicalNote

    rawOutput = askOllama(prompt)
    cleanedOutput = cleanOllamaOutput(rawOutput)
    print(cleanedOutput)
    print(answer)

    while True:
        try:
            matching = cleanOllamaOutput(askOllama("Return to me only a list of elements which are referring to the same thing in these two lists in JSON format. Do not include explanations to the text, only include the text itself. Here are the two lists: " + str(cleanedOutput) + ", " + str(answer)))
            break
        except:
            print()

    print(matching)

    true_positive += len(matching)
    false_positive += len([i for i in cleanedOutput if i not in matching])
    true_negative += clinicalNote.count(" ")/3 - len(matching) + len([i for i in answer if answer not in matching])*3
    false_negative += len([i for i in answer if answer not in matching])

    tempTruePositive = len(matching)
    tempFalsePositive = len([i for i in cleanedOutput if i not in matching])
    tempTrueNegative = clinicalNote.count(" ")/3 - len(matching) + len([i for i in answer if answer not in matching])*3
    tempFalseNegative = len([i for i in answer if answer not in matching])
    tempPrecision = tempTruePositive/(tempTruePositive + tempFalsePositive)
    tempRecall = tempTruePositive/(tempTruePositive + tempFalseNegative)
    try:    
        tempf1score = (2*tempPrecision*tempRecall)/(tempPrecision+tempRecall)
        print("SINGLE NOTE F1 SCORE: " + str(tempf1score))
    except:
        print("SINGLE NOTE F1 SCORE: 0")
    precision = true_positive/(true_positive + false_positive)
    recall = true_positive/(true_positive + false_negative)

    f1_score = (2*precision*recall)/(precision+recall)
    print("TOTAL F1 SCORE: " + str(f1_score))

precision = true_positive/(true_positive + false_positive)
recall = true_positive/(true_positive + false_negative)

f1_score = (2*precision*recall)/(precision+recall)
print(precision)
print(recall)
print(f1_score)