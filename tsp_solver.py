#necessary Libraries

import urllib.request
import requests

import collections
import csv

import numpy
import math
import random
import sys
import matplotlib.pyplot as plt

import datetime as dt
import urllib.request as ul
import re
import os.path



import datetime as dt

filename=sys.argv[1]

dir_path = os.path.join(os.getcwd(),"")
dir_path.replace(os.sep, '/')
dir_path = dir_path.replace(os.sep, '/')
filepath = os.path.join(dir_path, filename)
filethere = os.path.exists(filepath)
    
tsp     = { "EDGE_WEIGHT_TYPE" : None
           , "CITIES"           : []}

def main():

    if filethere==True:
        
        tspfile = open(filepath, 'r')
   
    else:
        ul.urlretrieve('http://elib.zib.de/pub/mp-testdata/tsp/tsplib/tsp/' + filename, filename)
        tspfile = open(filename, 'r')
    read_cities(tsp,tspfile)
    return tsp["CITIES"]


def read_cities(tsp,tspfile):
    
    f=0
    n=0
    i=0
    for line in tspfile.readlines():

        if re.match('EDGE_WEIGHT_TYPE.*', line):
            word = " ".join(line.split())
            word = word.split(' ')
            tsp['EDGE_WEIGHT_TYPE'] = word[2]

        elif re.match('NODE_COORD_SECTION.*', line):      
            f = 1
            continue
        elif re.match('EOF.*', line):
            break

        if (f==1 and tsp['EDGE_WEIGHT_TYPE']=="EUC_2D"):

            keyword = " ".join(line.split())
            keyword = keyword.split(' ')
            tsp["CITIES"].append((float(keyword[1]), float(keyword[2])))
                        
            

    if tsp["EDGE_WEIGHT_TYPE"] == "EUC_2D":

        n=0
        i=0
        cities = set()

        for line in tspfile:
            words   = collections.deque(line.split())
            if(n==1):
                if (words.popleft()=="EOF"): break
                x = float(words.popleft())
                y = float(words.popleft())
                i=i+1
                tsp["CITIES"].append((x,y))
                


            if(n==0):
                keyword = words.popleft().strip(": ")
                if (keyword == "NODE_COORD_SECTION"):
                     n=1
                        
cities=main()

class SimulatedAnnealing(object):
    def __init__(self,cities,stop_iter):
        self.cities=cities
        self.Num_nodes = len(cities) #Dimention of the cities is stored
        self.Temperature =  math.sqrt(self.Num_nodes) # Random intial temperature is considered
        self.stop_Temperature = 1e-8
        self.alpha = 0.999
        self.stop_iter = stop_iter
        
        self.best_tour=None
        self.best_fitness=float("Inf")
        self.fitness_list=[]
        self.iteration_now=1
        self.solution_history=[]
        
        self.nodes = [i for i in range(self.Num_nodes)]
        
        self.n=0
        
    def initial_tour_solution(self):
        
        #taking random node as initinal node to start
        curr_city = random.choice(self.nodes)
        tour = [curr_city]
        
        #All the other free nodes 
        free_cities = set(self.nodes)
        free_cities.remove(curr_city)
        
        while free_cities:
            neighbour_city = min(free_cities, key =lambda x:self.Euclidian_dist_cities(curr_city,x))
            free_cities.remove(neighbour_city)
            tour.append(neighbour_city)
            curr_city = neighbour_city
        
        current_fitness = self.distance(tour)
        
        if(current_fitness < self.best_fitness):
            self.best_fitness = current_fitness
            self.best_tour = tour
            
        return tour,current_fitness
    
    def Euclidian_dist_cities(self,citynodeA,citynodeB):
        
        # calculation the distance between two cities
        
        city_A, city_B = self.cities[citynodeA], self.cities[citynodeB]
        result = math.sqrt((city_A[0]-city_B[0])**2 + (city_A[1]-city_B[1])**2)
        return result
    
    def distance(self,tour):
        
        # to calculate the tour length
        curr_tour_length = 0
        for i in range(self.Num_nodes):
            curr_tour_length += self.Euclidian_dist_cities(tour[i % self.Num_nodes], tour[(i + 1) % self.Num_nodes])
        return curr_tour_length
    
    def probability(self, tour_fitness):
        
        p = math.exp(-abs(tour_fitness - self.curr_fitness)/(self.Temperature))
        return p
    
    def accept_solution(self, solution):
        
        tour_fitness = self.distance(solution)
        if(tour_fitness < self.curr_fitness):
            self.curr_fitness,self.curr_tour = tour_fitness,solution
            if(tour_fitness < self.best_fitness):
                self.best_fitness,self.best_tour = tour_fitness,solution
        
        else:
            if(random.random()<self.probability(tour_fitness)):
                self.curr_fitness,self.curr_tour = tour_fitness,solution
                
    
    def sim_anneal(self):
        
        start = dt.datetime.now()
        self.curr_tour,self.curr_fitness = self.initial_tour_solution()
        self.initial_fitness = self.curr_fitness
        
        print("Simulated anealing is starting ........")
        
        
        while((self.Temperature >= self.stop_Temperature) and (self.iteration_now < self.stop_iter)):
            
            tour = list(self.curr_tour)
            
            l = random.randint(2, self.Num_nodes - 1)
            i = random.randint(0, self.Num_nodes - l)
            tour[i : (i + l)] = reversed(tour[i : (i + l)])
            self.accept_solution(tour)
            self.Temperature *= self.alpha
            self.iteration_now += 1
            self.fitness_list.append(round(self.curr_fitness))
            self.solution_history.append(self.curr_tour)
            
        end = dt.datetime.now()  # time.time()
        self.executionTime = (end - start).seconds
        
        #print("length = ",self.iteration_now)
        #print("\nOPTIMAL TOUR = ",self.best_tour)
        print("\nCOST = ", self.best_fitness)
        print("\nExecution time = ",self.executionTime)
        print(start,end)
        return self.best_tour,self.best_fitness
    
    def plotting(self):
        
        plt.plot([i for i in range(len(self.fitness_list))], self.fitness_list)
        line_init = plt.axhline(y=self.initial_fitness, color='r', linestyle='--')
        line_min = plt.axhline(y=self.best_fitness, color='g', linestyle='--')
        plt.legend([line_init, line_min], ['Initial fitness', 'Optimized fitness'])
        plt.ylabel('fitness')
        plt.xlabel('Iteration')
        plt.show()
                      
sa = SimulatedAnnealing(cities, stop_iter=100000)
Optimal_tour,cost = sa.sim_anneal()  
print("\n\n")
sa.plotting()

import csv
with open("solution.csv","w") as f:
    wr = csv.writer(f,delimiter="\n")
    wr.writerow(Optimal_tour)
    f.close()
