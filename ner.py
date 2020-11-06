
# from transformers import pipeline

# nlp = pipeline("ner")

# # sequence = "Hugging Face Inc. is a company based in New York City. Its headquarters are in DUMBO, therefore very" \
# #            "close to the Manhattan Bridge which is visible from the window."
# sequence =  "The woman tolerated her friend's difficult behavior. it knew her friend was going through a hard time. The woman felt that her friend took advantage of her kindness."
# # word = "the women drank cofee"

# print(nlp(sequence))


import spacy 
  
nlp = spacy.load('en_core_web_sm') 
  
sentence = "punjab"
  
doc = nlp(sentence) 

for ent in doc.ents: 
    print(ent.text, ent.start_char, ent.end_char, ent.label_) 
