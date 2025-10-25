from csv_parser import parse_csv as pcsv
import random

class questionbox:

    def __init__(self):
        self.questionlist = []
    
    def addQuestion(self, que, ans):
        self.questionlist.append([que,ans])

    def addQuestion(self, que, corans, w1, w2, w3):
        self.questionlist.append([que,corans,w1,w2,w3])

    #gets array with question followed by three random answers and the correct one. the sixth element is which one is correct                                   
    def getQuestion(self):                                                                                                                                          
        corans = random.choice(self.questionlist)                                                                                                               
        wrongans = []                                                                                                                                          
        if (len(corans)==2):                                                                                                                                   
            for i in range(3):                                                                                                                                 
                acin=False                                                                                                                                     
                while(acin==False):                                                                                                                            
                    wrongan = random.choice(self.questionlist)[1]                                                                                              
                    if((wrongan != corans[1])and(wrongan not in wrongans)):                                                                                    
                        wrongans.append(wrongan)                                                                                                               
                        acin=True                                                                                                                              
        else:
             wrongans=[corans[2],corans[3],corans[4]]                                                                                                         
        questionset = [corans[0]]                                                                                                                              
        random.shuffle(wrongans)                                                                                                                               
        tru = random.randint(0,3)                                                                                                                              
        for i in range(4):
            if (i==tru):                                                                                                                                       
                questionset.append(corans[1])                                                                                                                  
            else:                                                                                                                                              
                questionset.append(wrongans.pop(0))                                                                                                            
        questionset.append(tru)                                                                                                                                
        return questionset

    #add questions from a CSV
    def getFromCSV(self, name):
        box = pcsv(name)
        while(len(box)>0):
            self.questionlist.append(box.pop(0))

    #remove a question with the question que
    def removeQuestionByQue(self, que):
        salt = []
        for i in range(len(self.questionlist)):
            salt.append(self.questionlist[i][0])
        if (que in salt):
            for i in range(len(self.questionlist)):
                if(que==self.questionlist[i][0]):
                    self.questionlist.pop(i)
                    return
        else:
            return    

    #remove a question by index
    def removeQuestionByIndex(self, I):
        self.questionlist.pop(I)

    #erase all questions
    def wipequestions(self):
        self.questionlist=[]


#checks if a question is correct    
def checkquestion(questionset, ans):
    return (questionset[5]==ans)
