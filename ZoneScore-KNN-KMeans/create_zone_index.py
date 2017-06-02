import sys
import sqlite3
import nltk
import os
import math

#need to download nltk/corpora/stopwords
#and              nltk/models/punkt from nltk.download()
punctuation = [",",".",";","(",")","#","!","$","%","&","'","''","'s","—","–","[","]","{","}","|-","|",":"]
stop_words = nltk.corpus.stopwords.words("english")
total_word_count = 0

def tokenize_insert(working_file, doc_id, conn):
    #tokenizes the words and then inserts them into the inverted index
    st = nltk.stem.LancasterStemmer()
    
    zone = 0
    position = 0
    for contents in working_file.readlines():
        zone += 1
    
        words = nltk.word_tokenize(contents)

        for token in words:
            #get rid of punctuation and stem the token
            if token not in punctuation:
                position += 1
                stemmed_word = st.stem(token)
                #insert into database
                if stemmed_word not in []:
                    if zone == 1:
                        try:
                            conn.execute('''INSERT INTO titles (title) VALUES ("{}")'''.format(stemmed_word))
                        except:
                            #if word is already in the table skip it
                            pass
                        conn.execute('''INSERT INTO instances VALUES ("{}","{}","{}","{}")'''.format(stemmed_word, doc_id, position, 1))
                    
                    else:
                        try:
                            conn.execute('''INSERT INTO words (word) VALUES ("{}")'''.format(stemmed_word))
                        except:
                            #if word is already in the table skip it
                            pass
                        conn.execute('''INSERT INTO instances VALUES ("{}","{}","{}","{}")'''.format(stemmed_word, doc_id, position, 0))
                
    #update the total amount of words in the corpus for idf score
    global total_word_count
    total_word_count += position
                
def create_drop_tables(conn):
    #drops all tables and creates new ones
    #3 tables and an index for faster boolean retrieval
    try:
        conn.execute("DROP TABLE words")
    except:
        pass    
    try:
        conn.execute("DROP TABLE instances")
    except:
        pass
    try:
        conn.execute("DROP INDEX idx")
    except:
        pass
    try:
        conn.execute("DROP TABLE titles")
    except:
        pass
       
    conn.execute('''CREATE TABLE titles
    (title TEXT PRIMARY KEY)''')
    conn.execute('''CREATE TABLE words 
    (word TEXT PRIMARY KEY)''')
    conn.execute('''CREATE TABLE instances 
    (word_id TEXT,
    doc_id INT, 
    word_index INT,
    zone INT,
    FOREIGN KEY (word_id) REFERENCES words(word))''')
    conn.execute('''CREATE INDEX idx on instances(word_id, doc_id, word_index)''')
                
def main():
    #open database and create tables
    
    #get index location
    try: 
        index_directory = sys.argv[2]
    except:
        print("No index directory given")
        exit()
    try:
        file_list = os.listdir(index_directory)
    except Exception as e:
        print("Index directory doesn't exsist")
        exit()
        
    os.chdir(index_directory)    
    conn = sqlite3.connect("zone_index.db")
    create_drop_tables(conn)
    
    #opening directory
    try:
        directory_name = sys.argv[1]
    except:
        print("No document directory given")
        exit()   
    #get list o f files in directory and change to that directory
    try:
        file_list = os.listdir(directory_name)
    except:
        print("Document directory doesn't exsist")
        exit()
    os.chdir(directory_name)
    
    #iterate over files
    for file in file_list:
        #get doc_id
        doc_id = file.split('.')[0]
        try:
            working_file = open(file, 'r')
            #file_contents = working_file.readlines()
            tokenize_insert(working_file, doc_id, conn)
            working_file.close()
        except Exception as e:
            print(e)
        
    #commit inverted index and close database
    conn.commit()
    conn.close()
        
if __name__ == '__main__':
    main()