import genetic 
import datetime
import unittest

class GuessPasswordTests(unittest.TestCase):
    geneset=" abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!.,"

    def test_Hello_World(self):
        target="Hello World!"
        self.guess_password(target)

    def test_I_am_Pramita_Kastha_a_keen_learner(self):
        target="I am Pramita Kastha, a keen learner."
        self.guess_password(target)

    def test_benchmark(self):
        genetic.Benchmark.run(self.test_I_am_Pramita_Kastha_a_keen_learner)

    def guess_password(self,target):
        startTime=datetime.datetime.now()

        def fnGetFitness(genes):
           return get_fitness(genes,target)

        def fnDisplay(candidate):
            display(candidate,startTime)

        optimalFitness=len(target)
        best=genetic.get_best(fnGetFitness,len(target),optimalFitness,self.geneset,fnDisplay)
        self.assertEqual(''.join(best.Genes),target)
        
def display(candidate,startTime):
    timeDiff=datetime.datetime.now()-startTime
    print("{0}\t{1}\t{2}".format(''.join(candidate.Genes),candidate.Fitness,str(timeDiff))) 

def get_fitness(genes,target):
    return sum(1 for expected, actual in zip(target,genes) if expected==actual)   

if __name__=='__main__':
    unittest.main()
