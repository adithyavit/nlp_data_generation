import pandas as pd
import spacy
import sys
spacy.prefer_gpu()
nlp = spacy.load("en_core_web_sm")
import random
import re
from readAndWriteData import write_json
data = pd.read_csv("balacopa-dev-all.csv")
count = 0


def select_replace(line, chunk):
    word = random.choice(tuple(chunk))
    pronoun = "it"
    line = re.sub(word, pronoun, line, flags=re.IGNORECASE)
    return line, word, pronoun

output_dict = {}
for row in data.itertuples(index=True, name='Pandas'):
    textp = row.p
    docp = nlp(textp)
    chunkp = [chunk.text.lower() for chunk in docp.noun_chunks]
    chunkp = set(chunkp)

    texta1 = row.a1
    doca1 = nlp(texta1)
    chunka1 = [chunk.text.lower() for chunk in doca1.noun_chunks]
    chunka1 = set(chunka1)

    texta2 = row.a2
    doca2 = nlp(texta2)
    chunka2 = [chunk.text.lower() for chunk in doca2.noun_chunks]
    chunka2 = set(chunka2)

    line = row.p+" "+row.a1+" "+row.a2
    intr1 = chunkp.intersection(chunka1)
    intr2 = chunka1.intersection(chunka2)
    intr3 = chunkp.intersection(chunka2)  

    total_set = intr1.union(intr2, intr3)
    total_length = len(total_set)

    if (total_length ==2):
        if(len(intr1)>0):
            line, referring_word, pronoun = select_replace(row.a1, chunka1)
            phrase = row.p+" "+line+" "+row.a2
            ans = referring_word
            option1 = total_set.pop()
            option2 = total_set.pop()
        elif(len(intr2)>0):
            line, referring_word, pronoun = select_replace(row.a2, chunka2)
            phrase = row.p+" "+row.a1+" "+line
            ans = referring_word
            option1 = total_set.pop()
            option2 = total_set.pop()
        elif(len(intr3)>0):
            line, referring_word, pronoun = select_replace(row.a2, chunka2)
            phrase = row.p+" "+row.a1+" "+line
            ans = referring_word
            option1 = total_set.pop()
            option2 = total_set.pop()

        count+=1
        each_output = {}
        each_output["Sentence"] = phrase
        each_output["Option1"] = option1
        each_output["Option2"] = option2
        each_output["Answer"] = ans
        output_dict[str(count)] = each_output
    write_json(output_dict, "model_output.json")
