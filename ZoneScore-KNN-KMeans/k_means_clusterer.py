import random
import sys
import os
import sqlite3
import math
import nltk

vector_distances = {}

word_list = []
tup_list = []
num_docs = 0
doc_vectors = []
final_vectors = []

seed_scores = []
grouped_score = {}

def group_documents():
    global grouped_score
    for seed_group in seed_scores:
        for score in seed_group:
            current_score = score[0]
            doc = score[1]
            current_seed = score[2]
            #if the doc already has a score but it is less than current_score, updated it to the new value
            if doc in grouped_score:
                if grouped_score[doc][0] < current_score:
                    grouped_score[doc] = (current_score, current_seed)
            #first time it has been seen
            else:
                grouped_score[doc] = (current_score, current_seed)
                
def for_testing():
    #os.chdir(index_directory)
    conn = sqlite3.connect("test_index.db")
    c = conn.cursor()
    return c
    

def tokenizer(terms):
    punctuation = [",",".",";","(",")","#","!","$","%","&","'","''","'s","—","–","[","]","{","}","|-","|", "\n"]
    st = nltk.stem.LancasterStemmer()
    words = nltk.word_tokenize(terms)

    words = [x for x in words if x not in punctuation]

    return words

def print_values(weights, k, scores, c):
    k = int(k)
    weights.sort()
    list1 = []
    printlist = []
    #if score == n than dont print the scores
    for i in range(0,k):
        value = weights.pop()
        string1 = str(str(value[1])+'('+str(value[0])+')')
        printlist.append(string1)
    return

def get_vector_length(c):
    #adds up the squares of all the tf values per document and then takes the squareroot to get the final normalized size.
    c.execute('''SELECT MAX(doc_id) from instances''')
    global num_docs
    num_docs = c.fetchone()
    num_docs = num_docs[0]
    for doc_id in range(1,num_docs+1):
        c.execute('''SELECT tf FROM tf_score
                    WHERE doc_id = {}'''.format(doc_id))
        #getting list of term frequencies for doc
        tflist = c.fetchall()
        global doc_vectors
        docid_tf = (doc_id,tflist)
        doc_vectors.append(docid_tf)

    for tup in doc_vectors:
        current_sum = 0
        #summing up all the squares of the tfs
        for tf in tup[1]:
            val = tf[0] * tf[0]
            current_sum += val
        #Taking the square root of the sum,     and storing in a list as a tuple with docid followed by the length
        global final_vectors
        sqrtval = math.sqrt(current_sum)
        newtup = (tup[0],sqrtval)
        final_vectors.append(newtup)
        current_sum = 0
    return



def get_weights(c, k, scores, terms, seed):
#calculate the tf-idf weigths and store in the instances table
    scores = {}
    global seed_scores
    global num_docs

    for term in terms:
        #calculating w_t_q
        try:
            c.execute('''SELECT df FROM words
                 WHERE word = "{}"'''.format(str(term)))
        except:
            c.execute('''SELECT df FROM words
                 WHERE word = '{}' '''.format(str(term)))
        df = c.fetchone()
        wtq = 0
        if df is None:
            df = 1
            w_t_q = 0
        else:
            df = df[0]
            w_t_q = math.log(num_docs / df)

        for doc in range(1,num_docs+1):
            try:
                c.execute('''SELECT word, idf, tf, doc_id
                        FROM words, tf_score
                        WHERE word = "{}" AND doc_id = {} AND word = word_tf'''.format(str(term),doc))
            except:
                c.execute('''SELECT word, idf, tf, doc_id
                        FROM words, tf_score
                        WHERE word = '{}' AND doc_id = {} AND word = word_tf'''.format(str(term),doc))

            #storing info in a tuple
            tup = c.fetchone()
            #if the term isnt in the doc so the tf is 0.
            #if it doesnt return a tuple, the term isnt there so tf-idf is set to 0
            if tup is None:
                tf_idf = 0
            #multiplying idf and tf together to get tf-idf
            else:
                idf = tup[1]
                tf = tup[2]
                tf_idf = idf * tf

            if doc in scores:
                scores[doc] += tf_idf * w_t_q
            else:
                scores[doc] = tf_idf * w_t_q
            

    answer = []

    for doc in scores:
        answer.append([scores[doc]/final_vectors[doc-1][1], doc, seed]) #/ by length

    seed_scores.append(answer)

    #print()
    #print(answer)
    #print()

    return answer


def compare_doc(doc1, doc2, c):
    score = 0
    #takes 2 doc id's and the connection as agrument
    #get terms from doc1
    c.execute('''SELECT word_id FROM instances WHERE doc_id == {}'''.format(doc1))
    results = c.fetchall()
    terms = []
    for i in results:
        terms.append(i[0])
        
    global seed_scores
    global num_docs

    for term in terms:
        #calculating w_t_q
        try:
            c.execute('''SELECT df FROM words
                 WHERE word = "{}"'''.format(str(term)))
        except:
            c.execute('''SELECT df FROM words
                 WHERE word = '{}' '''.format(str(term)))
        df = c.fetchone()
        wtq = 0
        if df is None:
            df = 1
            w_t_q = 0
        else:
            df = df[0]
            w_t_q = math.log(num_docs / df)
            
            
        try:
            c.execute('''SELECT word, idf, tf, doc_id
                    FROM words, tf_score
                    WHERE word = "{}" AND doc_id = {} AND word = word_tf'''.format(str(term),doc2))
        except:
            c.execute('''SELECT word, idf, tf, doc_id
                    FROM words, tf_score
                    WHERE word = '{}' AND doc_id = {} AND word = word_tf'''.format(str(term),doc2))
        tup = c.fetchone()
        #if the term isnt in the doc so the tf is 0.
        #if it doesnt return a tuple, the term isnt there so tf-idf is set to 0
        if tup is None:
            tf_idf = 0
        #multiplying idf and tf together to get tf-idf
        else:
            idf = tup[1]
            tf = tup[2]
            tf_idf = idf * tf
            
        score += tf_idf * w_t_q
    score = score/(final_vectors[doc2-1][1])
    
    return score
            
        
def get_groups(doc_list, seed_docs,c):
    #takes seed docs as argument returns the grouping of documents dictonary
    grouping = []
    group_dic = {}
    #get baseline grouping
    document = seed_docs[0]
    for comparing in doc_list:
        grouping.append([compare_doc(document, comparing, c), document, comparing])
    
    try:
        #for the documents left in the seed
        for document in seed_docs[1:]:
            #compare to each other
            for comparing in doc_list:
                score = compare_doc(document, comparing, c)
                if score > grouping[comparing][0]:
                    grouping[comparing] = [score, document, comparing]
    except:
        pass
                
    #sort into groups            
    for element in grouping:
        try:
            group_dic[element[1]].append(element[2])
        except:
            group_dic[element[1]] = [element[2]]
            
    return group_dic   
    
def get_docs(c):
    doc_list = []
    #get list of documents:
    c.execute('''SELECT DISTINCT(doc_id) FROM instances''')
    result = c.fetchall()
    for i in result:
        doc_list.append(i[0])
        
    return doc_list
    
def get_centroid(group,c,seeds):
    #takes a group and returns centroid of that group
    score = {}
    for member in group:
        #tuple is score and then document
        score[member] = 0
    for element in group:
        for neighbour in group:
            if element == neighbour:
                continue
            else:
                result = compare_doc(element, neighbour,c)
                score[element] += result
                    
    max_value = max(score.values())
    for key in score.keys():
        if score[key] == max_value:
            return(key)
    
                    
                
        
    
def init():
    #get values from command line and generate seed docs if necessary
    #open database
    try:
        index_directory = sys.argv[1]
    except:
        print("No index directory given")
        exit()
    try:
        file_list = os.listdir(index_directory)
    except Exception as e:
        print("Index directory doesn't exsist")
        exit()

    os.chdir(index_directory)
    conn = sqlite3.connect("inverted_index.db")
    c = conn.cursor()

    k_score = 0
    #get k
    try:
        k_score = int(sys.argv[2])
    except:
        print("k score not given")
        exit()

    #try get seed documents else randomly select them
    seed_docs = []
    #if there are no seed documents given
    if len(sys.argv) == 3:
        #generate the documents here
        c.execute('''SELECT DISTINCT(doc_id) FROM instances''')
        result = c.fetchall()
        doc_list = []
        for i in result:
            doc_list.append(i[0])
        for i in range(k_score):
            seed_docs.append(random.choice(doc_list))
    #if seed documents are given
    else:
        #make sure there enough k_scores given
        if len(sys.argv) - 3 == k_score:
            seed_docs = sys.argv[3:]
            seed_docs = list(map(int, seed_docs))
        else:
            print("Not enough seed documents supplied")
            exit()
            
    return c, k_score, seed_docs
    
def main():
    
    #intalize and get key values
    c, k_score, seed_docs = init()
    get_vector_length(c)
    doc_list = get_docs(c)
    grouping = {}
    
    #intalize old and new seed docs
    old_seed_docs = []
    new_seed_docs = seed_docs
    #while the old centroid is not equal to the new centroid
    while old_seed_docs != new_seed_docs:
        #intalize centroids inside while loop
        old_seed_docs = new_seed_docs
        new_seed_docs = []
        #get the grouping of the centroid
        grouping = get_groups(doc_list, old_seed_docs, c)
        #for each group get the new centroid and update
        for seed in old_seed_docs:
            new_seed = get_centroid(grouping[seed],c,new_seed_docs)
            new_seed_docs.append(new_seed)
    
    #print out the grouping 
    count = 1
    for key in grouping.keys():
        print(str(count)+"\t"+str(grouping[key]))
        count += 1
    
if __name__ == '__main__':
    main()
