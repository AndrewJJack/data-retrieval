import sys
import sqlite3
import nltk
import os

def get_word_list(c):
    c.execute('''SELECT word FROM words ORDER BY (word)''')
    word_list = c.fetchall()
    return(word_list)

def get_instances(c, word):
    c.execute('''SELECT doc_id, word_index FROM instances 
    WHERE word_id = "{}" '''.format(word[0])) 
    instances = c.fetchall()
    return instances
    
def print_results(c):
    #get list of words in database
    word_list = get_word_list(c)
    for word in word_list:
        #print out the word
        print(word[0],end = "\t")
        #check for all instances of that word 
        result = get_instances(c,word)
        
        #format documents so they print out in like example
        current_doc = result[0][0]
        doc_visited = False
        #tup is the doc_id followed by word_index
        for tup in result:
            if tup[0] == current_doc:
                #if documents hasn't been visted yet print doc and word_index
                if doc_visited == False:
                    print(str(tup[0])+':'+str(tup[1]), end = '')
                    doc_visited = True
                #else just print word_index
                else:
                    print(','+str(tup[1]), end = '')
            #new doc_id print ; and doc_id and word_index
            else:
                print(";", end='')
                print(str(tup[0])+':'+str(tup[1]), end = '')
                current_doc = tup[0]
        print("")
#            

def connect():
    #starts connection with inverted index
    try:
        conn = sqlite3.connect("inverted_index.db")
        c = conn.cursor()   
    except:
        print("Connection failed")
        exit()
    return c
    
def main():
    c = connect()
    print_results(c)
    
 
if __name__ == '__main__':
    main()
    
        

        
        
    
