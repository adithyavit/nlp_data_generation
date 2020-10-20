import pandas as pd
import spacy
nlp = spacy.load("en_core_web_sm")
import random
import re

data = pd.read_csv("balacopa-dev-all.csv")

def select_replace(line, chunk):
    word = random.choice(tuple(chunk))
    pronoun = "it"
    # line.replace(word, pronoun)
    line = re.sub(word, pronoun, line, flags=re.IGNORECASE)
    # print(line)
    return line, word, pronoun

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
    # print(chunkp)
    # print(chunka1)
    # print(chunka2)

    line = row.p+" "+row.a1+" "+row.a2

    # print(len(chunkp.intersection(chunka1)))
    # print(len(chunka1.intersection(chunka2)))
    # print(len(chunkp.intersection(chunka2)))
    if(len(chunkp.intersection(chunka1))>0):
        line, referring_word, pronoun = select_replace(row.a1, chunka1)
        print(row.p+" "+line+" "+row.a2)
        print(referring_word)
        print(pronoun)
        # continue
    if(len(chunka1.intersection(chunka2))>0):
        line, referring_word, pronoun = select_replace(row.a2, chunka2)
        print(row.p+" "+row.a1+" "+line)
        print(referring_word)
        print(pronoun)
        # continue
    if(len(chunkp.intersection(chunka2))>0):
        line, referring_word, pronoun = select_replace(row.a2, chunka2)
        print(row.p+" "+row.a1+" "+line)
        print(referring_word)
        print(pronoun)
        # continue
    # break
