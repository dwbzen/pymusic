'''
Created on Jul 9, 2021

@author: don_bacon
'''
import markovify

def main():
    """Test of the markovify package using the text of poems by Ferlinghetti.
        See https://pypi.org/project/markovify/
    """
    with open("C:/data/text/ferlinghetti.txt") as f:
        text = f.read()
    
    # Build the model.
    text_model = markovify.Text(text, state_size=2)
    
    # Print five randomly-generated sentences
    for i in range(5):
        print(f'{i}: {text_model.make_sentence()}' )
    
    # Print three randomly-generated sentences of no more than 280 characters
    for i in range(3):
        print(f'{i}  {text_model.make_short_sentence(280)}' )
    
    json_text = text_model.to_json()
    print(f'json: {json_text}')

if __name__ == '__main__':
    main()
    