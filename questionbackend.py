class questionbox:

    def __init__(self):
        self.questionlist = []
    
    #adds question with question que and answer ans
    def addQuestion(que, ans):
        self.questionlist.append([que,ans])

    #gets array with question followed by three random answers and the correct one. the sixth element is which one is correct 
    def getQuestion():
        corans = random.choice(self.questionlist)
        wrongans = []
        for i in range(3):
            acin=False
            while(acin==False):
                wrongan = random.choice(self.questionlist)[1]
                if((wrongan != corans[1])and(wrongan not in wrongans)):
                    wrongans.append(wrongan)
                    acin=True
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

    def removeQuestionByQue(que):
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

    def removeQuestionByIndex(I):
        self.questionlist.pop(I)

    def wipequestions():
        self.questionlist=[]

    
def checkquestion(questionset, ans):
    return (questionset[5]==ans)
