import random
import unittest
import datetime
import genetic
import lawnmower

class LawnmowerTests(unittest.TestCase):
    def run_with(self,geneSet,width,height,minGenes,maxGenes,expectedNumberOfInstructions,maxMutationRounds,fnCreateField,expectedNumberOfSteps):
        mowerStartLocation=lawnmower.Location(int(width/2),int(height/2))
        mowerStartDirection=lawnmower.Directions.South.value
        startTime=datetime.datetime.now()
        optimalFitness=Fitness(width*height,expectedNumberOfInstructions,expectedNumberOfSteps)
        
        def fnMutate(child):
            mutate(child,geneSet,minGenes,maxGenes,fnGetFitness,maxMutationRounds)
        
        def fnCreate():
            return create(geneSet,1,height)

        def fnEvaluate(instructions):
            program=Program(instructions)
            mower=lawnmower.Mower(mowerStartLocation,mowerStartDirection)
            field=fnCreateField()
            try:
                program.evaluate(mower,field)
            except RecursionError:
                pass
            return field,mower,program

        def fnGetFitness(genes):
            return get_fitness(genes,fnEvaluate)

        def fnDisplay(candidate):
            display(candidate,startTime,fnEvaluate)

        best=genetic.get_best(fnGetFitness,None,optimalFitness,None,fnDisplay,fnMutate,fnCreate,poolSize=10,crossover=crossover)
        self.assertTrue(not best.Fitness>optimalFitness)

    def test_mow_turn_repeat(self):
        width=height=8
        geneSet=[lambda: Mow(),lambda:Turn(),lambda:Repeat(random.randint(0,8),random.randint(0,8))]
        minGenes=3
        maxGenes=20
        maxMutationRounds=3
        expectedNumberOfInstructions=9
        expectedNumberOfSteps=88

        def fnCreateField():
            return lawnmower.ToroidField(width,height,lawnmower.FieldContents.Grass)
        
        self.run_with(geneSet,width,height,minGenes,maxGenes,expectedNumberOfInstructions,maxMutationRounds,fnCreateField,expectedNumberOfSteps)


def crossover(parent,otherParent):
    childGenes=parent[:]
    if len(parent)<=2 or len(otherParent)<2:
        return childGenes
    length=random.randint(1,len(parent)-2)
    start=random.randrange(0,len(parent)-length)
    childGenes[start:start+length]=otherParent[start:start+length]
    return childGenes

def display(candidate,startTime,fnEvaluate):
    field,mower,program=fnEvaluate(candidate.Genes)
    timeDiff=datetime.datetime.now()-startTime
    field.display(mower)
    print("{0}\t{1}".format(candidate.Fitness,str(timeDiff)))
    program.print()
    
class Fitness:
    TotalMowed=None
    TotalInstructions=None
    StepCount=None

    def __init__(self,totalMowed,totalInstructions,stepCount):
        self.TotalMowed=totalMowed
        self.TotalInstructions=totalInstructions
        self.StepCount=stepCount

    def __gt__(self,other):
        if self.TotalMowed!=other.TotalMowed:
            return self.TotalMowed>other.TotalMowed
        if self.StepCount!=other.StepCount:
            return self.StepCount<other.StepCount
        return self.TotalInstructions<other.TotalInstructions

    def __str__(self):
        return "{0} mowed with {1} instructions and {2} steps".format(self.TotalMowed,self.TotalInstructions,self.StepCount)
    
def get_fitness(genes,fnEvaluate):
    field,mower,_=fnEvaluate(genes)
    return Fitness(field.count_mowed(),len(genes),mower.StepCount)

def create(geneSet,minGenes,maxGenes):
    numGenes=random.randint(minGenes,maxGenes)
    genes=[random.choice(geneSet)() for _ in range(1,numGenes)]
    return genes

class Mow:
    def __init__(self):
        pass

    @staticmethod
    def execute(mower,field):
        mower.mow(field)

    def __str__(self):
        return "mow"

class Turn:
    def __init__(self):
        pass

    @staticmethod
    def execute(mower,field):
        mower.turn_left()

    def __str__(self):
        return "turn"

class Jump:
    Forward=None
    Right=None

    def __init__(self,forward,right):
        self.Forward=forward
        self.Right=right

    def execute(self,mower,field):
        mower.jump(field,self.Forward,self.Right)

    def __str__(self):
        return "jump({0},{1})".format(self.Forward,self.Right)

class Repeat:
    OpCount=None
    Times=None
    Ops=None

    def __init__(self,opCount,times):
        self.OpCount=opCount
        self.Times=times
        self.Ops=[]

    def execute(self,mower,field):
        for i in range(self.Times):
            for op in self.Ops:
                op.execute(mower,field)

    def __str__(self):
        return "repeat({0},{1})".format(' '.join(map(str,self.Ops)) if len(self.Ops)>0 else self.OpCount,self.Times)

    
class Program:
    Main=None

    def __init__(self,instructions):
        temp=instructions[:]
        for index in reversed(range(len(temp))):
            if type(temp[index]) is Repeat:
                start=index+1
                end=min(index+temp[index].OpCount+1,len(temp))
                temp[index].Ops=temp[start:end]
                del temp[start:end]
        self.Main=temp

    def evaluate(self,mower,field):
        for instruction in self.Main:
            instruction.execute(mower,field)

    def print(self):
        print(' '.join(map(str,self.Main)))

def mutate(genes,geneSet,minGenes,maxGenes,fnGetFitness,maxRounds):
    count=random.randint(1,maxRounds)
    initialFitness=fnGetFitness(genes)
    while count>0:
        count-=1
        if fnGetFitness(genes)>initialFitness:
            return
        adding=len(genes)==0 or (len(genes)<maxGenes and random.randint(0,5)==0)
        if adding:
            genes.append(random.choice(geneSet)())
            continue

        removing=len(genes)>minGenes and random.randint(0,50)==0
        if removing:
            index=random.randrange(0,len(genes))
            del genes[index]
            continue

        index=random.randrange(0,len(genes))
        genes[index]=random.choice(geneSet)()

if __name__=='__main__':
    unittest.main()
            
