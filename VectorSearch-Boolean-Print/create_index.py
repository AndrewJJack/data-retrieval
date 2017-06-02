import sys
import sqlite3
import nltk
import os
import math

#need to download nltk/corpora/stopwords
#and              nltk/models/punkt from nltk.download()
punctuation = [",",".",";","(",")","#","!","$","%","&","'","''","'s","—","–","[","]","{","}","|-","|"]
stop_words = nltk.corpus.stopwords.words("english")
total_word_count = 0
document_count = 0

def tokenize_insert(contents, doc_id, conn):
    #tokenizes the words and then inserts them into the inverted index
    st = nltk.stem.LancasterStemmer()
    words = nltk.word_tokenize(contents)
    position = 0
    #iterate over words
    for token in words:
        #get rid of punctuation and stem the token
        if token not in punctuation:
            position += 1
            stemmed_word = st.stem(token)
            #insert into database
            if stemmed_word not in []:
                try:
                    conn.execute('''INSERT INTO words (word) VALUES ("{}")'''.format(stemmed_word))
                except:
                    #if word is already in the table skip it
                    pass
                conn.execute('''INSERT INTO instances VALUES ("{}","{}","{}")'''.format(stemmed_word, doc_id, position)) 
    
    calculate_tf(conn, doc_id, position)

    #update the total amount of words in the corpus for idf score
    global total_word_count
    total_word_count += position
    
def calculate_tf(conn, doc_id, word_count):
    #calculate the tf scores and store them in the tf_score table
    c = conn.cursor() 
    #select all the words and count of that word from instances table
    c.execute('''SELECT word_id, COUNT(word_id) FROM instances WHERE doc_id = {} GROUP BY word_id'''.format(doc_id))
    word_list = c.fetchall()
    
    #iterate over word list and insert values into tf_score
    for element in word_list:
        conn.execute('''INSERT INTO tf_score VALUES("{}","{}","{}")'''.format(element[0], doc_id, 1 + math.log10(element[1])))
        
def calculate_idf(conn):
    #calculate the idf and store it in the words table
    global total_word_count
    c = conn.cursor()
    #get a list of all the words to iterate through
    c.execute('''SELECT word FROM words''')
    word_list = c.fetchall()
    
    for element in word_list:
        c.execute('''SELECT COUNT(DISTINCT(doc_id)) FROM instances WHERE word_id == "{}"'''.format(element[0]))
        count = c.fetchall()[0][0]
        try:
            c.execute('''UPDATE words SET idf = {} WHERE word == '{}' '''.format(math.log10(document_count/count), element[0]))
        #if the word has single quotes in it it will raise an error
        except:
            c.execute('''UPDATE words SET idf = {} WHERE word == "{}" '''.format(math.log10(document_count/count), element[0]))
        

            
        #store df in table 
        try:
            c.execute('''UPDATE words SET df = {} WHERE word == '{}' '''.format(count, element[0]))
        #if the word has single quotes in it it will raise an error
        except:
            c.execute('''UPDATE words SET df = {} WHERE word == "{}" '''.format(count, element[0]))
        
                
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
        conn.execute("DROP TABLE tf_score")
    except:
        pass
    try:
        conn.execute("DROP INDEX idx")
    except:
        pass
        
    conn.execute('''CREATE TABLE words 
    (word TEXT PRIMARY KEY,
    idf INT, df INT)''')
    conn.execute('''CREATE TABLE instances 
    (word_id TEXT,
    doc_id INT, 
    word_index INT,
    FOREIGN KEY (word_id) REFERENCES words(word))''')
    conn.execute('''CREATE TABLE tf_score 
    (word_tf TEXT, 
    doc_id INT, 
    tf INT,
    FOREIGN KEY (word_tf) REFERENCES words(word))''')
    conn.execute('''CREATE INDEX idx on instances(word_id, doc_id, word_index)''')
                
def main():
    #open database and create tables
    conn = sqlite3.connect("inverted_index.db")
    create_drop_tables(conn)
    
    #opening directory
    try:
        directory_name = sys.argv[1]
    except:
        print("No file input given")
        exit()   
    if directory_name not in os.listdir():
        print("Not a valid directory name")
        exit()

    #get list o f files in directory and change to that directory   
    file_list = os.listdir(directory_name)
    os.chdir(directory_name)
    
    global document_count
    #iterate over files
    for file in file_list:
        document_count += 1
        #get doc_id
        doc_id = file.split('_')[1]
        try:
            working_file = open(file, 'r')
            file_contents = working_file.read()
            tokenize_insert(file_contents, doc_id, conn)
            working_file.close()
        except:
            print("File not readable")
        
    #commit inverted index and close database
    calculate_idf(conn)
    conn.commit()
    conn.close()
        
if __name__ == '__main__':
    main()