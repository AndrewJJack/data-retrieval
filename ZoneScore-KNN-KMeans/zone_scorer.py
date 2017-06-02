import sys
import nltk
import sqlite3
import os

punctuation = [",",".",";","(",")","#","!","$","%","&","'","''","'s","—","–","[","]","{","}","|-","|"]
stop_words = nltk.corpus.stopwords.words("english")

def convert_reverse_RPN(query):
    #implements shunting-yard algorthim
    #takes boolean query and returns reverse rpn
    #must do query in reverse order because and and or are evaluated left to right
    queue = []
    operands = []
    
    #for all boolean queries
    for element in reversed(query):
        #if element is a operand
        if "AND" in element or "OR" in element:
            operands.append(element)
        #if there is a start of a bracket
        elif "]" in element:
            #count opening brackets and append to operands
            sets = element.count("]")
            for x in range (0, sets):
                operands.append("]")
            queue.append(element.replace("]",""))
        #end of bracket
        elif "[" in element:
            #add operands that were in the brackets to the queue
            sets = element.count("[")
            queue.append(element.replace("[",''))
            oper = operands.pop()
            queue.append(oper)
            for x in range (0, sets):
                while oper != "]":
                    oper = operands.pop()
                    queue.append(oper)
                queue.pop()
        else:
            queue.append(element)

    #append the rest of operands onto queue
    while len(operands) != 0:
        queue.append(operands.pop())
  
    return queue

def tokenize(word):
    st = nltk.stem.LancasterStemmer()
    stemmed_word = st.stem(word)  
    return stemmed_word
    
def eval_phrase(conn, phrase, title):
    #this is probably a complicated way to do this but it words
    #... and I couldn't think of another way at the time
    #takes a phrase and returns posting list for that phrase
    words = phrase.split()
    postings_list = []
    dic_list = []
    
    terms = 0
    for word in words:
        terms += 1
    
    #create a list of dictionaries key = doc_id values = word_index
    for word in words:
        conn.execute('''SELECT doc_id, word_index FROM instances WHERE word_id = "{}" '''.format(tokenize(word)))
        posting = conn.fetchall()
        dic = {}
        for doc in posting:
            if doc[0] in dic.keys():
                interm_list = dic.get(doc[0])
                interm_list.append(doc[1])
                dic[doc[0]] = interm_list
            else:
                dic[doc[0]] = [doc[1]]
        dic_list.append(dic)
         
    #list with all matching postings with doc_id and word_index
    list_post = []
    #get all the key and value pairs for first dictonary (word)
    for key in dic_list[0].keys():
        for value in dic_list[0].get(key):
            #check the other dictonaries to see if they have keys correct number away
            current_dic = 0
            for dic in dic_list[1:]:
                current_dic += 1
                #compare first and second dictonaries to get a starting point
                if current_dic == 1:
                    try:
                        if (value + current_dic) in dic[key]:
                            list_post.append([key, value])
                        else:
                            break
                    except:
                        pass
                #check other dictonaries to see if they have complete phrase
                else:
                    try:
                        if (value + current_dic) in dic[key] and [key, value] in list_post:
                            pass
                        else:
                            list_post.remove([key, value])
                    #if doc doesn't only contains first words of phrase        
                    except:
                        try:
                            list_post.remove([key, value])
                        except:
                            pass

    count = 0
    #get rid of the phrases that are not in the same zone
    for phrase in list_post:
        count = phrase[1]
        doc = phrase[0]
        for i in range(0,terms):
            count += i
            conn.execute('''SELECT zone FROM instances WHERE doc_id == {} AND word_index == {}'''.format(doc, count))
            title_check = conn.fetchone()[0]
            if title_check != title:
                try:
                    list_post.remove(phrase)
                except:
                    pass
        
    #delete duplicates and return postings list
    for doc in list_post:
        if doc[0] not in postings_list:
            postings_list.append(doc[0])
    return postings_list
    
    
def get_postings(conn, word, title):
    #takes stemmed word and returns posting list of docs that contain the word
    conn.execute('''SELECT doc_id FROM instances WHERE word_id = "{}" AND zone == {} GROUP BY doc_id'''.format(word, title))
    postings = conn.fetchall()
    postings_list = []
    for i in postings:
        postings_list.append(i[0])
    return postings_list
    
def connect(index_directory):
    #starts connection with inverted index
    try:
        file_list = os.listdir(index_directory)
        os.chdir(index_directory) 
    except Exception as e:
        print("Index directory doesn't exsist")
    
    try:
        conn = sqlite3.connect("zone_index.db")
        c = conn.cursor()   
    except:
        print("Connection failed")
        exit()
    return c
    
    
def and_lists(list1, list2):
    return set(list1).intersection(list2)

def or_lists(list1, list2):
    return set(list1).union(list2)

def get_scores():
    k_score = 0
    g_score = 0
    query = ""
    
    #connect to index 
    index_directory = sys.argv[1]
    conn = connect(index_directory)
    
    #get k score
    try:
        k_score = sys.argv[2]
    except:
        print("No K score given")
        exit()
        
    #get g score
    try:
        g_score = sys.argv[3]
    except:
        print("No G score given")
        exit()
        
    #get query
    try:
        query = sys.argv[4:]
    except:
        print("No query given")
        exit()
        
    return k_score, g_score, query, conn
    
def eval_query(rpn_eval, conn, title):
    eval_stack = [] 
    for element in rpn_eval:
        #if it is not an operand
        if not ("AND" in element or "OR" in element):
            #if it is a phrase
            if len(element.split()) > 1:
                eval_stack.append(eval_phrase(conn, element, title))
            #if it is just a word
            else:
                eval_stack.append(get_postings(conn, (tokenize(element)), title))
        #else it is an operand
        else:
            list1 = eval_stack.pop()
            list2 = eval_stack.pop()
            if "AND" in element:
                eval_stack.append(and_lists(list1, list2))
            if "OR" in element:
                eval_stack.append(or_lists(list1, list2)) 
                
    return eval_stack
def zoneScore(g, q, title, body):
    scores = {}

    #trimming 'AND' and 'OR' terms. trimming code from http://stackoverflow.com/questions/2793324/is-there-a-simple-way-to-delete-a-list-element-by-value
    q = [x for x in q if x != 'AND']
    q = [x for x in q if x != 'OR']

    #calculating the relative weight of each term in the query so max score per doc = 1

    #adding the value of g per doc for the titles
    for doc in title:
        if doc in scores:
            scores[doc] += g
        else:
            scores[doc] = g 

    #adding the value of (1-g) per doc for the body
    for doc in body:
        if doc in scores:
            scores[doc] += (1-g) 
        else:
            scores[doc] = (1-g) 
    
    return scores

def main():
    
    k_score, g_score, query, conn = get_scores()
    
    #get order to evaluate query in 
    rpn_eval = convert_reverse_RPN(query)
    #start evaluating query
    try:
        #get docs with query in title and docs with query in body
        title_stack = eval_query(rpn_eval, conn, 1)[0]
        body_stack = eval_query(rpn_eval, conn, 0)[0]
        scores = zoneScore(float(g_score), rpn_eval, title_stack, body_stack)
    
    except Exception as e:
        print(e)
        print("Ill-defined query")
        exit()        
     
    #print scores to screen
    scores_list = []
    #sort dictonary
    for key, value in scores.items():
        tup= (value, key)
        scores_list.append(tup)
    scores_list.sort(reverse = True)
    #print list up to k
    for i in  range(0,int(k_score)):
        try:
            print("doc"+str(scores_list[i][1]) + " " + str(scores_list[i][0]))
        except Exception as e:
            pass
                        
if __name__ == "__main__":          
    main()
    