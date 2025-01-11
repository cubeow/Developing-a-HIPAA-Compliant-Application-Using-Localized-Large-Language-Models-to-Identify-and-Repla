import json
import glob
import time
import re
import os

prompt = """Suppose you are a clinician who has just asked questions with a patient who has a serious medical condition and are now writing your notes. Here is their general information: Make sure you generate one note without stigmatizing language and the other with stigmatizing language. You may generate these numbers and qualtative things in a realistic way. Output by replacing only my text with the brackets and by keeping the categories preceding the colon. Make it so that the note always contains stigmatizing language. Also make sure to output whether or not the note is stigmatizing, under the category "contains-stigmatizing-language". Such stigmatizing language found in clinical notes include: in general, Labeling Patients, and examples are: Sickler, Narcotic dependent, Narcotic, Alcoholic, Diabetic.
Judgmental or Biased Descriptions: "In our ED frequently", "Cursing at nurse", “Difficult, “challenging”, and “resistant”, “Inconsistent historian”, Going on a whole rant about how the patient is inconsistent and unreliable, “Unable to give a clear timeline”, “Contradicting oneself”, Blame-Oriented Statements: Compliance/compliant, Medication nonadherence, “Compliance issues”, “Unable to accomplish something due to a patient being noncompliant”. Documentation of Refusal: “Declined completing an exam”, “Refused an exam” Mention of poor socioeconomic status: “Mentions that he was hanging out around McDonald’s with his friends”. Choose one of these categories or even multiple of them. If you choose the labeling patients, make sure to label them multiple times. If you choose the judgmental or biased descriptions, make sure to use the words and similar words to "Dificult", "Challenging", and "Resistant" many times and keep a subtle negative tone in the background. If you choose the Blame-oriented statements, make sure to use a multitude of those words and similar words many times. If you choose the documentatino of refusal, make sure to use the refuse words many times. If you choose the poor socioeconomic status, which is really rare and subtle, just mention it like once. So to restate, just make sure that you choose one or multiple of these and make sure to say these stigmatizing words around 7 times in the entire note. 
 Additionally, make sure to have a list of all of the stigmatizing terms and phrases used for stigmatizing languages, if used, and put them under the category of "stigmatizing language". Make sure that all of the categories are separated line by line, and that only the bullet points or numbered lists are indented, not the normal categories. Make sure to un-indent the categories after a numbered list or bullet points. And to bold each category: Contains-stigmatizing-language: [stigmatizing language contained? yes/no] Stigmatizing language used: [stigmatizing language used] Admission date: [mm/dd/yyyy] Discharge date: [mm/dd/yyyy] Date of Birth: [mm/dd/yyyy] Sex: [F/M] Service: [MEDICINE] Allergies: [allergies or no known allergies] Attending: ___ Chief Complaint: [Problem that the patient has] Major Surgical or Invasive Procedure: [surgical or invasive procedure] History of Present Illness: [Talks about just their present illness and any question that they asked about it and any events such as food poisoning] Past Medical History: [Any past conditions and usage of drugs or cigarettes] Social History: [social history] Family History: [Siblings, knowledge of whether or not there is a past medical history with the illness that she has currently] Physical Exam: VS [number results] General [general] HEENT [qualitative results] Neck [qualitative results] CV [qualitative results] Lungs [qualitative results] Abdomen [qualitative results] GU [qualitative results] Ext [qualitative results] Neuro [qualitative results] Pertinent Results: [Have multiple timestamps detailing the procedures and things that have happened] Brief Hospital Course: [Mentions mental health, characteristics of their medical condition which may be of concern.] Medications on Admission: [A numbered list, usually around 8] Discharge medications: [A numbered list, usually around 8] Discharge Disposition: [one word location like home or something] Discharge Diagnosis: [their medical condition] Discharge Condition: Mental Status: [Mental status] Activity Status: [Activity status] Discharge Instructions: [150 words], detail specific procedures they did and explain why the procedures were performed. Ask them to take medications daily and also recommend a diet. Also, give them further instructions on any potential doctors they will have to meet to schedule additional appointments. Farewell ending. Followup Instructions: [Followup instructions]
"""

allPatientDataFilePaths = glob.glob(r"/Users/sagewong/git/StigmatizingLanguageProject/Synthea/synthea_sample_data_fhir_r4_sep2019/fhir/*")
allPrompts = []
basicPatientInformation = {}
for patientPath in allPatientDataFilePaths:
    with open(patientPath) as file:
        # reads the first patient data and parses as json
        firstPatientData = json.load(file)

    basicPatientInformation.clear()

    try:
        basicPatientInformation["condition"] = firstPatientData["entry"][4]["resource"]["code"]["text"]
    except:
        None
    try:
        basicPatientInformation["gender"] = firstPatientData["entry"][2]["resource"]["gender"]
    except:
        None
    try:
        basicPatientInformation["name"] = re.sub(r'\d', '', firstPatientData["entry"][3]["resource"]["subject"]["display"])
    except:
        None
    try:
        basicPatientInformation["birthday"] = firstPatientData["entry"][0]["resource"]["birthDate"]
    except:
        None
    try:
        basicPatientInformation["race"] = firstPatientData["entry"][0]["resource"]["extension"][0]["extension"][0]["valueCoding"]["display"]
    except:
        None
    try:
        basicPatientInformation["hispanic"] = firstPatientData["entry"][0]["resource"]["extension"][1]["extension"][1]["valueString"]
    except:
        None
    try:
        if "Pain severity" not in firstPatientData["entry"][5]["resource"]["code"]["coding"][0]["display"]:
            basicPatientInformation["history"] = firstPatientData["entry"][5]["resource"]["code"]["coding"][0]["display"]
    except:
        None
    try:
        basicPatientInformation["device"] = firstPatientData["entry"][6]["resource"]["deviceName"][0]["name"]
    except:
        None
    
    syntheaData = str(basicPatientInformation)
    promptnew = prompt[:174] + syntheaData + prompt[174:]
    allPrompts.append(promptnew)
allPrompts = allPrompts[18:101]
completion = await client.chat.completions.create(model="gpt-4-turbo-preview", messages=[{"role":"user", "content": newQuestion}])
print(completion.choices[0].message.content)
