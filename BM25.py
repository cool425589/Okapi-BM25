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
#windos請輸入C:/或者D:/
path ='C:/'
basepath = os.path.join(os.path.sep, path , 'Users', 'M10615079','Desktop','Homework1')
#檔案平均長度
avgdl = 0 
#總檔案數目
D = 0
#數值越低則飽和的過程越快速
k1 = 1.2
#數值越低則飽和的過程越快速
k3 = 2
#較高的b會增加文檔長度對得分的影響
b = 0.75
#較高的Delta會增加文檔長度對得分的影響
Delta = 0.5
#所有檔案 ( 1維 key->term )
term_in_D_dictionary = {}
#個別檔案 ( 2維 documentname->(term,num) )
term_in_d_dictionary = {}
#個別query ( 2維 documentname->(term,num) )
term_in_d_query = {}
#個別檔案 ( 2維 documentname->(term,tf) )
tf_in_d_dictionary = {}
#個別檔案 ( 2維 documentname->(term,tf) )
tf_in_d_query = {}
#所有檔案 ( 1維 term->idf )
idf_in_D_dictionary = {}
#所有檔案 ( 1維 documentname->lengh )
length_in_D_dictionary = {}
#所有query ( 1維 queryname->lengh )
length_in_Q_dictionary ={}
#所有檔案 BM25分數 ( 2維 queryname->(document,BM25) )
BM25_in_D_dictionary = {}
#單檔案 BM25分數 ( 1維 document-> BM25 )
BM25_in_d_dictionary = {}
#所有檔案 排名文件 ( 2維 query ->(key,document) )
answer_in_D_dictionary = {}
#總答案成功數
totalanswers = 0
#前次總答案成功數
pre_totalanswers = 0
#目前最佳參數
best_k1 = 0
best_k3 = 0
best_b = 0

def readfile(filename):
    #目標目錄下的資料夾
    Readingfile = filename
    #記錄讀檔數量
    readnum = 0
    #曆尋資料夾下的文件
    for filename in os.listdir(os.getcwd()):
        readnum += 1
        #給予下層要cd的路徑
        relative_path = os.path.join(os.path.sep,os.getcwd(),filename)
        #檔案是否存在且是否為文件
        if os.path.isfile(relative_path):
            #file所參考到的物件，不管有肥有發生異常，最後會被自動清除
            with open(relative_path, 'rb') as f:
                try:
                    f = open(relative_path)    #打開文件
                    data = f.read().split()   # 讀取內容
                    if fnmatch.fnmatch(Readingfile, 'Document'):
                        #計算 doucment內的檔案長度
                        GetLen_doc(data,filename)
                        #文件總word
                        term_in_d_dictionary[filename] = DocumentVector(data, filename);
                    elif fnmatch.fnmatch(Readingfile, 'Query'):
                        #計算 query內的檔案長度
                        GetLen_query(data,filename)
                        term_in_d_query[filename] = DocumentVector(data,filename);
                except Exception as e:
                    print (strHello)
                    print (e)
    #目標開始資料夾/filename 曆尋結束，返回目前路徑的上一層
    os.chdir("..")


def GetLen_doc(read_data,filename):
    #文件總word = 總word數 - '-1'的數量
    tatoal_length = len(read_data) - read_data.count('-1')
    #檔案數放入length_in_D_dictionary
    global length_in_D_dictionary
    length_in_D_dictionary[filename] = tatoal_length

def GetLen_query(read_data,filename):
    #文件總word = 總word數 - '-1'的數量
    tatoal_length = len(read_data) - read_data.count('-1')
    #檔案數放入length_in_D_dictionary
    global length_in_Q_dictionary
    length_in_Q_dictionary[filename] = tatoal_length

def DocumentVector(read_data,documentname):
    from collections import defaultdict
    temp = defaultdict(int)
    #計算term重複數量
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
    #idf是否存在辭海
    idf = idf_in_D_dictionary.get(term,-1)
    #idf no exist in dic
    if idf == -1:
        #包含此term的檔案數量
        has_term_d_number = 0
        #進入個別檔案的dic
        for documentName, d_dictionary in term_in_d_dictionary.items():
            #判斷term是否存在document
            if  term in d_dictionary :
                has_term_d_number += 1
        idf = math.log10( (D-has_term_d_number+0.5)/(has_term_d_number+0.5))
        #idf不可為負
        if idf < 0:
            idf = 0
        #將以計算過idf得idf存入辭海
        idf_in_D_dictionary[term] = idf

    return idf

def Getavgl():
    global avgdl
    #計算document平均長度
    for name,length in length_in_D_dictionary.items():
        avgdl+=length   
    avgdl = avgdl/D

def BM25(query,document,queryname,documentname):
    #BM25
    BM25 = 0
    #document長度
    d = 0
    #拿出document長度
    d = length_in_D_dictionary.get(documentname, 0)
    #拿出query中的term
    for term ,tf in query.items():     
        #不處理-1
        if term != '-1':
            idf_termq = 0.0
            tf_termq_d = 0.0
            #拿出term的tf，若document沒有此term，回傳0
            tf_termq_d = Get_tf(term,documentname)
            #拿出term的tf，若document沒有此term，回傳0
            tf_term_q = Get_tf_query(term,queryname)
            weighting_for_query = ( (k3 + 1) * tf_term_q ) / ( k3 + tf_term_q )
            #若tf = 0，直接返回0
            if tf_termq_d != 0 and weighting_for_query != 0:
                #拿出term的idf，若辭海(所有檔案)沒有此term，回傳0
                idf_termq = idf_term(term, term_in_d_dictionary)
                #BM25公式
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
        #排序BM25_dictionary
        rank = sorted(BM25_dictionary.items(), key=operator.itemgetter(1))
        #反轉BM25_dictionary
        rank.reverse()
        alist = answer_in_D_dictionary.get(rankqueryname,[])
        #印出前20結果
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

#cd 至目標開始資料夾
os.chdir(basepath)
for filename in os.listdir(os.getcwd()):
    #給予下層要cd的路徑
    relative_path = os.path.join(os.path.sep,os.getcwd(),filename)
    #檔案是否存在且是否為目錄
    if os.path.isdir(relative_path):
        #開始找query與document
        #cd 目標開始資料夾/filename
        os.chdir(filename)
        #是否為query dict
        if fnmatch.fnmatch(filename, 'Query'):
            readfile(filename)
        elif fnmatch.fnmatch(filename, 'Document'):
            readfile(filename)
def getanswer():
    for filename in os.listdir(os.getcwd()):
        #給予下層要cd的路徑
        relative_path = os.path.join(os.path.sep,os.getcwd(),filename)
        #檔案是否存在且是否為文件
        if os.path.isfile(relative_path):
            if fnmatch.fnmatch(filename, 'answer.txt'):
                #file所參考到的物件，不管有沒有發生異常，最後會被自動清除
                with open(relative_path, 'rb') as f:
                    try:
                            f = open(relative_path)    #打開文件
                            data = f.read().split()   # 讀取內容
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
    #曆尋query，算出BM25分數
    #取得|D|數量
    global D
    D = len(term_in_d_dictionary)
    #先取得平均長度
    Getavgl()
    for queryname, query_dictionary in term_in_d_query.items():
        BM25_in_d_dictionary ={}
        i+=1
        d_num = 0
        for documentname , document_dictionary in term_in_d_dictionary.items():
            d_num += 1
            BM25scrore = 0.0
            #得到BM25分數
            BM25scrore = BM25(query_dictionary,document_dictionary,queryname,documentname)
            #放入1維dictionary
            BM25_in_d_dictionary[documentname] = BM25scrore
        #放入2維dictionary
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
#開始
training()


