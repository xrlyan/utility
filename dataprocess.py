#!/usr/bin/python

import re
import csv
import math
import os

import numpy as np
import matplotlib.pyplot as plt
import scipy as sp
import scipy.stats

#mode_name=['First','Second','Third','Fourth']
mode_name=['SemiSpace','GenCopy','MarkSweep','GenMS','RefCount','GenRF']


class benchmark():

    ## hapValue or shadowValue saves the execut time for each mem_size and each mod_name
    ## 3 for mem_size; 4 for jikesrvm mode
    heap_count=2
    rvm_count =6
    hapValue=[[]*rvm_count]*heap_count
    shadowValue=[[]*rvm_count]*heap_count
    hapValue_delta=[[]*rvm_count]*heap_count
    shadowValue_delta=[[]*rvm_count]*heap_count
    iternation=10
    mem_size=[]
    data_type="time"
    confidence=0.95
    dataPath="040214" 
    
    def __init__(self, name,mem_size,dataPath):
        '''Initializes the person's data.'''
        self.name = name
        self.dataPath = dataPath
        self.mem_size = mem_size
 #       print '(We are running %s)' % self.name

            
    def setFastValue(self,mode):
        tempValue=[[]*rvm_count]*heap_count
        result_list=self.setValue(mode)
        tempValue=result_list[0]
        for m in range(1,self.iternation):
            for i in range(heap_count):
                for j in range (rvm_count): 
                    if result_list[m][i][j] < tempValue[i][j]:
                        tempValue[i][j]= result_list[m][i][j]
        #print tempValue
        return tempValue;

    def getValue(self,mode):
        '''This function get the data value from the file and save them in a format '''
        dataFile=self.dataPath+"/domu/"+mode+"-dacapo-"+self.name+"-result"
        f = open(dataFile)
        lines = f.readlines()
        regex=r'\d\d+'
        data_list=[]
        for line in lines:
            match=re.findall(regex,line)
            if match:
                data_list.append(match)
        f.close()
        
        result_list=np.array(data_list,dtype=int).reshape(self.iternation,self.heap_count,self.rvm_count)

        return result_list

    def dataProcess(self,mode):
        '''get the average value and confidence '''
        source_list=self.getValue(mode)        
        avage_list=np.mean(source_list,axis=0)

        std_list=np.std(source_list,axis=0)
        delta_list = std_list * sp.stats.t._ppf((1+self.confidence)/2., self.iternation-1)

        return std_list,delta_list
    
    def createCsv(self):
#        print self.hapValue

        source_list_hap=self.getValue("hap")
        print source_list_hap
        avage_list_hap=np.mean(source_list_hap,axis=0)
        self.hapValue=avage_list_hap
        std_list_hap=np.std(source_list_hap,axis=0)
        delta_list_hap= std_list_hap * sp.stats.t._ppf((1+self.confidence)/2., self.iternation-1)
        self.hapValue_delta=delta_list_hap
        
        source_list_shadow=self.getValue("native")
        avage_list_shadow=np.mean(source_list_shadow,axis=0)
        self.shadowValue=avage_list_shadow
        std_list_shadow=np.std(source_list_shadow,axis=0)
        delta_list_shadow= std_list_shadow * sp.stats.t._ppf((1+self.confidence)/2., self.iternation-1)
        self.shadowValue_delta=delta_list_shadow

        para="_"+self.data_type
        filetype=".csv"

        filename=self.dataPath+"/csv/"+self.name+para+filetype
        fw = open(filename,'wb')
        csvfile=csv.writer(fw)
        
        ##format: hap(mode1_size1 mode1_size2 mode1_size3)
        title_name=['Heap size','SemiSpace-hap','SemiSpace-native','GenCopy-hap','GenCopy-native','MarkSweep-hap','MarkSweep-native','GenMS-hap','GenMS-native','RefCount-hap','RefCount-native','GenRF-hap','GenRF-native'] 
        csvfile.writerow(title_name)
        for i in range(self.heap_count):
            for j in range(self.iternation):
                csvfile.writerow([self.mem_size[i],source_list_hap[j][i][0],source_list_shadow[j][i][0],source_list_hap[j][i][1],source_list_shadow[j][i][1],source_list_hap[j][i][2],source_list_shadow[j][i][2],source_list_hap[j][i][3],source_list_shadow[j][i][3],source_list_hap[j][i][4],source_list_shadow[j][i][4],source_list_hap[j][i][5],source_list_shadow[j][i][5]])
                              
        mean_name=['Mean']*9
        csvfile.writerow(mean_name)
        for i in range(self.heap_count):
            csvfile.writerow([self.mem_size[i],avage_list_hap[i][0],avage_list_shadow[i][0],avage_list_hap[i][1],avage_list_shadow[i][1],avage_list_hap[i][2],avage_list_shadow[i][2],avage_list_hap[i][3],avage_list_shadow[i][3],avage_list_hap[i][4],avage_list_shadow[i][4],avage_list_hap[i][5],avage_list_shadow[i][5]])

        std_name=['Std']*9
        csvfile.writerow(std_name)
        for i in range(self.heap_count):
            csvfile.writerow([self.mem_size[i],std_list_hap[i][0],std_list_shadow[i][0],std_list_hap[i][1],std_list_shadow[i][1],std_list_hap[i][2],std_list_shadow[i][2],std_list_hap[i][3],std_list_shadow[i][3],std_list_hap[i][4],std_list_shadow[i][4],std_list_hap[i][5],std_list_shadow[i][5]])

        coefficient_name=['Coefficient']*9    
        csvfile.writerow(coefficient_name)
        csvfile.writerow([sp.stats.t._ppf((1+self.confidence)/2., self.iternation-1)]*9)
            
        delta_name=['Delta']*9
        csvfile.writerow(delta_name)
        for i in range(self.heap_count):
            csvfile.writerow([self.mem_size[i],delta_list_hap[i][0],delta_list_shadow[i][0],delta_list_hap[i][1],delta_list_shadow[i][1],delta_list_hap[i][2],delta_list_shadow[i][2],delta_list_hap[i][3],delta_list_shadow[i][3],delta_list_hap[i][4],delta_list_shadow[i][4],delta_list_hap[i][5],delta_list_shadow[i][5]])

        fw.close()

    def drawPic(self):
        N = 6
        pic_name = self.dataPath+"/png/"+self.name + '_'+self.data_type+'.png'
        ind = np.arange(N)  # the x locations for the groups
        width = 0.1      # the width of the bars
        fig, ax = plt.subplots()
        x=[0]*6
        xData=[x]*4
        xData[0]=[int(self.hapValue[0][0]),int(self.hapValue[0][1]),int(self.hapValue[0][2]),int(self.hapValue[0][3]),int(self.hapValue[0][4]),int(self.hapValue[0][5])]
        xData[1]=[int(self.shadowValue[0][0]),int(self.shadowValue[0][1]),int(self.shadowValue[0][2]),int(self.shadowValue[0][3]),int(self.shadowValue[0][4]),int(self.shadowValue[0][5])]
        xData[2]=[int(self.hapValue[1][0]),int(self.hapValue[1][1]),int(self.hapValue[1][2]),int(self.hapValue[1][3]),int(self.hapValue[1][4]),int(self.hapValue[1][5])]
        xData[3]=[int(self.shadowValue[1][0]),int(self.shadowValue[1][1]),int(self.shadowValue[1][2]),int(self.shadowValue[1][3]),int(self.shadowValue[1][4]),int(self.shadowValue[1][5])]

        stdData=[x]*4
        stdData[0]=[float(self.hapValue_delta[0][0]),float(self.hapValue_delta[0][1]),float(self.hapValue_delta[0][2]),float(self.hapValue_delta[0][3]),float(self.hapValue_delta[0][4]),float(self.hapValue_delta[0][5])]
        stdData[1]=[float(self.shadowValue_delta[0][0]),float(self.shadowValue_delta[0][1]),float(self.shadowValue_delta[0][2]),float(self.shadowValue_delta[0][3]),float(self.shadowValue_delta[0][4]),float(self.shadowValue_delta[0][5])]
        stdData[2]=[float(self.hapValue_delta[1][0]),float(self.hapValue_delta[1][1]),float(self.hapValue_delta[1][2]),float(self.hapValue_delta[1][3]),float(self.hapValue_delta[1][4]),float(self.hapValue_delta[1][5])]
        stdData[3]=[float(self.shadowValue_delta[1][0]),float(self.shadowValue_delta[1][1]),float(self.shadowValue_delta[1][2]),float(self.shadowValue_delta[1][3]),float(self.shadowValue_delta[1][4]),float(self.shadowValue_delta[1][5])]

    
        rects1 = ax.bar(ind, xData[0], width, color='red',yerr=stdData[0])
        rects2 = ax.bar(ind+width, xData[1], width, color='yellow',yerr=stdData[1])
        rects3 = ax.bar(ind+width+width, xData[2], width, color='blue',yerr=stdData[2])
        rects4 = ax.bar(ind+width+width+width, xData[3], width, color='green',yerr=stdData[3])
    # add some
        ax.set_ylabel(self.data_type)
        ax.set_title(self.name+'-'+self.data_type)
        ax.set_xticks(ind+width)
        ax.set_xticklabels( mode_name )

        lable_name1='Hap-'+self.mem_size[0]
        lable_name3='Hap-'+self.mem_size[1]
        lable_name2='Native-'+self.mem_size[0]
        lable_name4='Native-'+self.mem_size[1]
 
        lgd=ax.legend((rects1[0],rects2[0],rects3[0],rects4[0]),(lable_name1,lable_name2,lable_name3,lable_name4),loc=2, bbox_to_anchor=(1.05, 1), borderaxespad=0)  
        
        plt.savefig(pic_name,bbox_extra_artists=(lgd,), bbox_inches='tight')

def checkDirectory(dataPath):

    csv_path = dataPath+"/csv"
    png_path = dataPath+"/png"
    path_list=[csv_path,png_path]
    for path in path_list:
        isExists=os.path.exists(path)
        if not isExists:
            print path+' is created'
            os.makedirs(path)
        else:
            print path+' has been created, need to be deleted'
            os.system('rm -rf ' + path)
            print 'new '+path+' is created'           
            os.makedirs(path)

def createBenchmark(name,mem_size,dataPath):
    test=benchmark(name,mem_size,dataPath)
    test.iternation=10
    print "create csv here"
    test.createCsv()
    test.drawPic()

def OneTest(dataPath):
    dacapo_name1=["antlr", "luindex"]
    dacapo_name2=["bloat", "jython", "lusearch", "pmd", "fop"]
    dacapo_name3=["hsqldb"]
    dacapo_name=[dacapo_name1,dacapo_name2,dacapo_name3]
    mem=[["64m","128m"],["128m","256m"],["512m","1024m"]]
    for i in range(3):
        for name in dacapo_name[i]:
            createBenchmark(name,mem[i],dataPath)
                
if __name__ == '__main__':
#   run the spefic class of benchmark

    dataPath_list=["050814"]
 
    for dataPath in dataPath_list:
        checkDirectory(dataPath)
        OneTest(dataPath)

    print "Everything is done, Please check the results!"
