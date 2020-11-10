
import pandas as pd
import spacy
import sys
spacy.prefer_gpu()
nlp = spacy.load("en_core_web_sm")
import random
import re
from random import seed
import time
import random
from readAndWriteData import write_json, write_csv_from_dict
data = pd.read_csv("balacopa-dev-all.csv")
# data = pd.read_csv("balacopa-dev-small.csv")
count = 0

pronoun_set = set()
output_dict = {}
# output_dict = set()

male_set = {'her brother', 'his older brother', 'he', 'his brother', 'the man','him', 'the boy'}
female_set = {'her', 'her sister', 'the girl', 'her mother','her daughter','she','the woman','his mother'}
neutral_set = {'the suspect', 'the police officer','his classmate','the rider', 'the assailant', 'the student', 'the child', 
'a player', 'the physician', 'the scar','his enemy', 'the police', 'the bully', 'the cook', 'i', 'the customer',
 'the therapist', 'the teacher', 'the caller','the president','her friend','the celebrity','the mayor','the baby'}
object_set = {'the gum', 'the computer', 'the door','the puddle', 'it', 'my foot', 'the chair', 'her finger',
'the bottle', 'the shirt', 'the paperclip', 'the dog', 'the railing', 'her hair', 'college', 'the floor', 
'the book', 'my yard', 'the puzzle', 'the clay','the button', 'his back', 'the church', 'the moon','the disease','the question','his theory','the gift','loose change','the tablecloth','the thread','the room','the jar','the pond',
'the fabric', 'the desk','the liquid', 'the slide',"the patient's arm",'the bill','his toys','the air conditioner','the hamburger','his pocket',
'the bowling ball','school'}
plural_set = {'the audience', 'my hands', 'the rules', 'her parents','the parents','the children','they'}
neutral_self_set = {'i', 'we', 'them'}  

def select_replace_neutral(line, chunk, he_she, word):
    pronoun = he_she
    line = re.sub(word, pronoun, line, flags=re.IGNORECASE)
    return line, word, pronoun

def select_replace(line, chunk):
    pronoun = "it"
    is_neutral=False
    word = random.choice(tuple(chunk))
    if(word in male_set): pronoun ="he"
    if(word in female_set): pronoun ="she"
    if(word in neutral_set): 
        pronoun ="he"
        is_neutral = True
    if(word in object_set): pronoun ="it"
    if(word in plural_set): pronoun ="they"
    if(word in neutral_self_set): pronoun = word

    line = re.sub(word, pronoun, line, flags=re.IGNORECASE)
    return line, word, pronoun, is_neutral

def prepare_output(each_output, phrase, option1, option2, ans, pronoun, offset1, offset2, pronoun_offset):
    each_output['ID'] = "development_new"+str(count)
    each_output["Text"] = phrase
    each_output["Pronoun"] = pronoun
    each_output["Pronoun-offset"] = pronoun_offset
    each_output["A"] = option1
    each_output["A-offset"] = offset1
    if(ans==option1): 
        each_output["A-coref"] = True
    elif(ans==option2): 
        each_output["A-coref"] = False
    each_output["B"] = option2
    each_output["B-offset"] = offset2
    if(ans==option2): 
        each_output["B-coref"] = True
    elif(ans==option1): 
        each_output["B-coref"] = False
    each_output['URL'] = "no url"
    # each_output["Answer"] = ans


def get_values(referring_word, union_set, phrase):
    ans = referring_word
    option1 = ans
    union_set.discard(ans)
    option2 = union_set.pop()
    seed(time.time())
    randval = random.randint(0,1)
    if(randval == 0):
        option1, option2 = option2, option1
    offset1 = phrase.lower().find(option1)
    offset2 = phrase.lower().find(option2)
    return ans, option1, option2, offset1, offset2

def set_values(ans, option1, option2, phrase, pronoun, offset1, offset2, pronoun_offset):
    global count
    global pronoun_set
    global output_dict
    count+=1
    each_output = {}
    prepare_output(each_output, phrase, option1, option2, ans, pronoun, offset1, offset2, pronoun_offset)
    pronoun_set.add(ans)
    output_dict[str(count)] = each_output
    # output_dict.add(each_output)


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
    # print(total_set)
    union_set = chunkp.union(chunka1).union(chunka2)
    # change it >0 afterwards
    if (total_length ==2):

        while(len(union_set)>1):
            # print(union_set)
            # print(len(intr1), len(intr2), len(intr3))
            if(len(intr1)>0):
                line, referring_word, pronoun,is_neutral = select_replace(row.a1, intr1)
                if(is_neutral):
                    line, referring_word, pronoun = select_replace_neutral(row.a1, intr1,"he", referring_word)
                    phrase = row.p+" "+line+" "+row.a2
                    ans, option1, option2, offset1, offset2 = get_values(referring_word, union_set, phrase)
                    pronoun_offset = phrase.lower().find(pronoun)
                    set_values(ans, option1, option2, phrase, pronoun, offset1, offset2, pronoun_offset)
                    
                    line, referring_word, pronoun = select_replace_neutral(row.a1, intr1,"she", referring_word)
                    phrase = row.p+" "+line+" "+row.a2
                    pronoun_offset = phrase.lower().find(pronoun)
                    set_values(ans, option1, option2, phrase, pronoun, offset1, offset2, pronoun_offset)
                else:   
                    phrase = row.p+" "+line+" "+row.a2
                    ans, option1, option2, offset1, offset2 = get_values(referring_word, union_set, phrase)
                    pronoun_offset = phrase.lower().find(pronoun)
                    set_values(ans, option1, option2, phrase, pronoun, offset1, offset2, pronoun_offset)


            elif(len(intr2)>0):
                line, referring_word, pronoun, is_neutral = select_replace(row.a2, intr2)
                if(is_neutral):
                    line, referring_word, pronoun = select_replace_neutral(row.a1, intr1,"he", referring_word)
                    phrase = row.p+" "+row.a1+" "+line
                    ans, option1, option2, offset1, offset2 = get_values(referring_word, union_set, phrase)
                    pronoun_offset = phrase.lower().find(pronoun)
                    set_values(ans, option1, option2, phrase, pronoun, offset1, offset2, pronoun_offset)

                    line, referring_word, pronoun = select_replace_neutral(row.a1, intr1,"she", referring_word)
                    phrase = row.p+" "+row.a1+" "+line
                    pronoun_offset = phrase.lower().find(pronoun)
                    set_values(ans, option1, option2, phrase, pronoun, offset1, offset2, pronoun_offset)
                else:
                    phrase = row.p+" "+row.a1+" "+line
                    ans, option1, option2, offset1, offset2 = get_values(referring_word, union_set, phrase)
                    pronoun_offset = phrase.lower().find(pronoun)
                    set_values(ans, option1, option2, phrase, pronoun, offset1, offset2, pronoun_offset)

            elif(len(intr2)>0):
                line, referring_word, pronoun, is_neutral = select_replace(row.a2, intr2)
                if(is_neutral):
                    line, referring_word, pronoun = select_replace_neutral(row.a1, intr1,"he", referring_word)
                    phrase = row.p+" "+row.a1+" "+line
                    ans, option1, option2, offset1, offset2 = get_values(referring_word, union_set, phrase)
                    pronoun_offset = phrase.lower().find(pronoun)
                    set_values(ans, option1, option2, phrase, pronoun, offset1, offset2, pronoun_offset)

                    line, referring_word, pronoun = select_replace_neutral(row.a1, intr1,"she", referring_word)
                    phrase = row.p+" "+row.a1+" "+line
                    pronoun_offset = phrase.lower().find(pronoun)
                    set_values(ans, option1, option2, phrase, pronoun, offset1, offset2, pronoun_offset)
                else:
                    phrase = row.p+" "+row.a1+" "+line
                    ans, option1, option2, offset1, offset2 = get_values(referring_word, union_set, phrase)
                    pronoun_offset = phrase.lower().find(pronoun)
                    set_values(ans, option1, option2, phrase, pronoun, offset1, offset2, pronoun_offset)                 
            else:
                break
    
    output_df = pd.DataFrame.from_dict(output_dict, orient='index')
    # output_df.drop(output_df.columns[[0]], axis=1) 
    output_df = output_df.loc[:, ~output_df.columns.str.contains('^Unnamed')]
    # print(output_df.columns)
    output_df.to_csv('model_output.csv')
    write_json(output_dict, "model_output.json")
    # write_csv_from_dict(output_dict, "model_output.csv")


# print(len(male_set)+len(female_set)+len(neutral_set)+len(object_set)+len(plural_set)+len(neutral_self_set))
# combined_set = (male_set).union(female_set).union(neutral_set).union(object_set).union(plural_set).union(neutral_self_set)
# print(len(pronoun_set))
# # pronoun_set.remove(combined_set)
# # print(pronoun_set)
# print(combined_set.difference(pronoun_set))
# print(pronoun_set.difference(combined_set))