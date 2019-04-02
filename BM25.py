# !/usr/bin/python 
# -*-coding:utf-8 -*- 
import os
import fnmatch
import math
import copy
import operator
import time
start = time.time()
file_data = []
#windos�п�JC:/�Ϊ�D:/
path ='C:/'
basepath = os.path.join(os.path.sep, path , 'Users', 'M10615079','Desktop','Homework1')
#�ɮץ�������
avgdl = 0 
#�`�ɮ׼ƥ�
D = 0
#�ƭȶV�C�h���M���L�{�V�ֳt
k1 = 1.2
#�ƭȶV�C�h���M���L�{�V�ֳt
k3 = 2
#������b�|�W�[���ɪ��׹�o�����v�T
b = 0.75
#������Delta�|�W�[���ɪ��׹�o�����v�T
Delta = 0.5
#�Ҧ��ɮ� ( 1�� key->term )
term_in_D_dictionary = {}
#�ӧO�ɮ� ( 2�� documentname->(term,num) )
term_in_d_dictionary = {}
#�ӧOquery ( 2�� documentname->(term,num) )
term_in_d_query = {}
#�ӧO�ɮ� ( 2�� documentname->(term,tf) )
tf_in_d_dictionary = {}
#�ӧO�ɮ� ( 2�� documentname->(term,tf) )
tf_in_d_query = {}
#�Ҧ��ɮ� ( 1�� term->idf )
idf_in_D_dictionary = {}
#�Ҧ��ɮ� ( 1�� documentname->lengh )
length_in_D_dictionary = {}
#�Ҧ�query ( 1�� queryname->lengh )
length_in_Q_dictionary ={}
#�Ҧ��ɮ� BM25���� ( 2�� queryname->(document,BM25) )
BM25_in_D_dictionary = {}
#���ɮ� BM25���� ( 1�� document-> BM25 )
BM25_in_d_dictionary = {}
#�Ҧ��ɮ� �ƦW��� ( 2�� query ->(key,document) )
answer_in_D_dictionary = {}
#�`���צ��\��
totalanswers = 0
#�e���`���צ��\��
pre_totalanswers = 0
#�ثe�̨ΰѼ�
best_k1 = 0
best_k3 = 0
best_b = 0

def readfile(filename):
    #�ؼХؿ��U����Ƨ�
    Readingfile = filename
    #�O��Ū�ɼƶq
    readnum = 0
    #��M��Ƨ��U�����
    for filename in os.listdir(os.getcwd()):
        readnum += 1
        #�����U�h�ncd�����|
        relative_path = os.path.join(os.path.sep,os.getcwd(),filename)
        #�ɮ׬O�_�s�b�B�O�_�����
        if os.path.isfile(relative_path):
            #file�ҰѦҨ쪺����A���ަ��Φ��o�Ͳ��`�A�̫�|�Q�۰ʲM��
            with open(relative_path, 'rb') as f:
                try:
                    f = open(relative_path)    #���}���
                    data = f.read().split()   # Ū�����e
                    if fnmatch.fnmatch(Readingfile, 'Document'):
                        #�p�� doucment�����ɮת���
                        GetLen_doc(data,filename)
                        #����`word
                        term_in_d_dictionary[filename] = DocumentVector(data, filename);
                    elif fnmatch.fnmatch(Readingfile, 'Query'):
                        #�p�� query�����ɮת���
                        GetLen_query(data,filename)
                        term_in_d_query[filename] = DocumentVector(data,filename);
                except Exception as e:
                    print (strHello)
                    print (e)
    #�ؼж}�l��Ƨ�/filename ��M�����A��^�ثe���|���W�@�h
    os.chdir("..")


def GetLen_doc(read_data,filename):
    #����`word = �`word�� - '-1'���ƶq
    tatoal_length = len(read_data) - read_data.count('-1')
    #�ɮ׼Ʃ�Jlength_in_D_dictionary
    global length_in_D_dictionary
    length_in_D_dictionary[filename] = tatoal_length

def GetLen_query(read_data,filename):
    #����`word = �`word�� - '-1'���ƶq
    tatoal_length = len(read_data) - read_data.count('-1')
    #�ɮ׼Ʃ�Jlength_in_D_dictionary
    global length_in_Q_dictionary
    length_in_Q_dictionary[filename] = tatoal_length

def DocumentVector(read_data,documentname):
    from collections import defaultdict
    temp = defaultdict(int)
    #�p��term���Ƽƶq
    for term in read_data:
        temp[term] += 1
    return temp

def Get_tf(term,documentname):
    d_dic = term_in_d_dictionary.get(documentname,0)
    term_count = d_dic.get(term,0)
    if term_count !=0:
        word_count = length_in_D_dictionary.get(documentname,0)
        tf = term_count/word_count
    else :
        tf = 0
    return tf

def Get_tf_query(term,queryname):
    q_dic = term_in_d_query.get(queryname,0)
    term_count = q_dic.get(term,0)
    if term_count !=0:
        word_count = length_in_Q_dictionary.get(queryname,0)
        tf = term_count/word_count
    else :
        tf = 0
    return tf

def idf_term(term,term_in_d_dictionary):
    #idf�O�_�s�b���
    idf = idf_in_D_dictionary.get(term,-1)
    #idf no exist in dic
    if idf == -1:
        #�]�t��term���ɮ׼ƶq
        has_term_d_number = 0
        #�i�J�ӧO�ɮת�dic
        for documentName, d_dictionary in term_in_d_dictionary.items():
            #�P�_term�O�_�s�bdocument
            if  term in d_dictionary :
                has_term_d_number += 1
        idf = math.log10( (D-has_term_d_number+0.5)/(has_term_d_number+0.5))
        #idf���i���t
        if idf < 0:
            idf = 0
        #�N�H�p��Lidf�oidf�s�J���
        idf_in_D_dictionary[term] = idf

    return idf

def Getavgl():
    global avgdl
    #�p��document��������
    for name,length in length_in_D_dictionary.items():
        avgdl+=length   
    avgdl = avgdl/D

def BM25(query,document,queryname,documentname):
    #BM25
    BM25 = 0
    #document����
    d = 0
    #���Xdocument����
    d = length_in_D_dictionary.get(documentname, 0)
    #���Xquery����term
    for term ,tf in query.items():     
        #���B�z-1
        if term != '-1':
            idf_termq = 0.0
            tf_termq_d = 0.0
            #���Xterm��tf�A�Ydocument�S����term�A�^��0
            tf_termq_d = Get_tf(term,documentname)
            #���Xterm��tf�A�Ydocument�S����term�A�^��0
            tf_term_q = Get_tf_query(term,queryname)
            weighting_for_query = ( (k3 + 1) * tf_term_q ) / ( k3 + tf_term_q )
            #�Ytf = 0�A������^0
            if tf_termq_d != 0 and weighting_for_query != 0:
                #���Xterm��idf�A�Y���(�Ҧ��ɮ�)�S����term�A�^��0
                idf_termq = idf_term(term, term_in_d_dictionary)
                #BM25����
                tf_termq_d_pr = idf_termq/(1-b+b*d/avgdl)
                k1_tf = 0
                if tf_termq_d_pr > 0 :
                    k1_tf = ( (k1+1)*(tf_termq_d_pr + Delta) ) / ( k1 + ( tf_termq_d_pr + Delta ) )
                BM25 += ( idf_termq *  k1_tf   * weighting_for_query )
               # BM25 += ( idf_termq * (  ( tf_termq_d * (k1+1) ) / ( tf_termq_d + ( k1 * ( 1-b+b*d/avgdl ) ) ) ) * weighting_for_query )
    return BM25

def rankdocument(BM25_in_D_dictionary):
    getanswer()
    answer = 0
    alist = []
    global totalanswers
    totalanswers = 0
    for rankqueryname, BM25_dictionary in BM25_in_D_dictionary.items():
        #�Ƨ�BM25_dictionary
        rank = sorted(BM25_dictionary.items(), key=operator.itemgetter(1))
        #����BM25_dictionary
        rank.reverse()
        alist = answer_in_D_dictionary.get(rankqueryname,[])
        #�L�X�e20���G
        answer = 0
        for num in range(0,14):
            if alist.count(rank[num][0]) == 1:
                alist.remove(rank[num][0])
                answer+=1
        totalanswers += answer
        for take_num in range(0,len(alist)):
            remain_BM25 = BM25_dictionary.get(alist[take_num],0)

    global pre_totalanswers
    if totalanswers > pre_totalanswers:
        pre_totalanswers = totalanswers
        best_k1 = k1
        best_k3 = k3
        best_b = b
        print ("k1 : " + str(k1) )
        print ("k3 : " + str(k3) )
        print ("b : " + str(b) )
        print ("totalanswers : " + str(totalanswers) )

#cd �ܥؼж}�l��Ƨ�
os.chdir(basepath)
for filename in os.listdir(os.getcwd()):
    #�����U�h�ncd�����|
    relative_path = os.path.join(os.path.sep,os.getcwd(),filename)
    #�ɮ׬O�_�s�b�B�O�_���ؿ�
    if os.path.isdir(relative_path):
        #�}�l��query�Pdocument
        #cd �ؼж}�l��Ƨ�/filename
        os.chdir(filename)
        #�O�_��query dict
        if fnmatch.fnmatch(filename, 'Query'):
            readfile(filename)
        elif fnmatch.fnmatch(filename, 'Document'):
            readfile(filename)
def getanswer():
    for filename in os.listdir(os.getcwd()):
        #�����U�h�ncd�����|
        relative_path = os.path.join(os.path.sep,os.getcwd(),filename)
        #�ɮ׬O�_�s�b�B�O�_�����
        if os.path.isfile(relative_path):
            if fnmatch.fnmatch(filename, 'answer.txt'):
                #file�ҰѦҨ쪺����A���ަ��S���o�Ͳ��`�A�̫�|�Q�۰ʲM��
                with open(relative_path, 'rb') as f:
                    try:
                            f = open(relative_path)    #���}���
                            data = f.read().split()   # Ū�����e
                            list = []
                            i = 0
                            queryname = ''
                            for itemvalue in data:
                                if itemvalue == 'Query' :
                                    global answer_in_D_dictionary
                                    answer_in_D_dictionary[queryname] = list
                                    i = 0
                                    queryname = ''
                                    list = []
                                elif i > 15 :
                                    continue
                                elif i < 1 or i ==2:
                                    i+=1
                                elif i == 1:
                                    i+=1
                                    queryname = itemvalue
                                elif i > 2:
                                    i+=1
                                    list.append(itemvalue)
                            print (" ")
                    except Exception as e:
                        print (strHello)
                        print (e)
def queryByBM25():
    i = 0
    #��Mquery�A��XBM25����
    #���o|D|�ƶq
    global D
    D = len(term_in_d_dictionary)
    #�����o��������
    Getavgl()
    for queryname, query_dictionary in term_in_d_query.items():
        BM25_in_d_dictionary ={}
        i+=1
        d_num = 0
        for documentname , document_dictionary in term_in_d_dictionary.items():
            d_num += 1
            BM25scrore = 0.0
            #�o��BM25����
            BM25scrore = BM25(query_dictionary,document_dictionary,queryname,documentname)
            #��J1��dictionary
            BM25_in_d_dictionary[documentname] = BM25scrore
        #��J2��dictionary
        global BM25_in_D_dictionary
        BM25_in_D_dictionary[queryname] = BM25_in_d_dictionary
    end = time.time()
    elapsed = end - start
    rankdocument(BM25_in_D_dictionary)     

def training():
    for i in range(0,10):
        for j in range(0,10):
            for k in range(0,10):
                global k1
                k1 = 1+(i/10)
                global k3
                k3 = 1+(j/10)
                global b
                b = (k/10)
                queryByBM25()              
#�}�l
training()


