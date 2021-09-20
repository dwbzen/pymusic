'''
Created on Jul 9, 2021

@author: don_bacon
'''
import markovify

if __name__ == '__main__':
    with open("C:/data/text/ferlinghetti.txt") as f:
        text = f.read()
    
    # Build the model.
    text_model = markovify.Text(text)
    
    # Print five randomly-generated sentences
    for i in range(5):
        print(text_model.make_sentence())
    
    # Print three randomly-generated sentences of no more than 280 characters
    for i in range(3):
        print(text_model.make_short_sentence(280))
    
    json = text_model.to_json()