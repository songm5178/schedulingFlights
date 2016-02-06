# Pyomo Template

# These two lines are required.  DO NOT REMOVE

from __future__ import division
from pyomo.environ import *
from pyomo.opt import *

# indicate your data file name here

datafile = "flights.dat"
# Instantiate the model

model = AbstractModel()
model.name = "Modified Maximum Cost Network Flow Model"

# Define sets

# Nodes in the network
model.Nodes = Set()
# Network arcs
model.FlightArcs = Set(within=model.Nodes*model.Nodes)
model.NonFlightArcs = Set(within=model.Nodes*model.Nodes)
model.EndOfDayBridgeArcs = Set(within=model.Nodes*model.Nodes)
model.Arcs = model.FlightArcs | model.NonFlightArcs #| model.EndOfDayBridgeArcs

model.BalanceNodes = Set(within=model.Nodes*model.Nodes)

# Define Parameters

# Revenue per unit flow across each arc
model.Revenue = Param(model.Arcs)#, within=NonNegativeReals)

# Flight numbers for descriptive purposes
model.FlightNumber = Param(model.Arcs)

model.nPlanes = Param(within=NonNegativeIntegers)
model.Balance = Param(model.Nodes)

# Flow balance through each node:
# Positive balance means more into node than outgoing
# Negative balance means more outgoing from node than coming into
# Zero balance means Flow in == Flow Out
# Should have Total Balance = 0

# model.balance = Param(model.Nodes)

# Define Variables 

# The flow over each arc
model.x = Var(model.Arcs, within=NonNegativeReals)


## Define Objective
# Minimize the cost of the flow across the network
def TotalRevenue(M):
    return sum(M.Revenue[i,j] * M.x[i,j] for (i, j) in M.Arcs)
model.total = Objective(rule=TotalRevenue, sense=maximize)


## Constraints

# Enforce an upper limit on the flow across each flight arc
def binary_var(M, i, j):
    return M.x[i,j] <= 1
model.limit = Constraint(model.FlightArcs, rule=binary_var)

# Enforce flow balance through each node
def flow_rule(M, k):
    FlowIn  = sum(M.x[i,j] for (i,j) in M.Arcs if j == k)
    FlowOut = sum(M.x[i,j] for (i,j) in M.Arcs if i == k)
    return FlowIn - FlowOut == M.Balance[k]
model.FlowBalance = Constraint(model.Nodes, rule=flow_rule)

# def end_of_day_locations(M, k, l):
#     FlowIn  = sum(M.x[i,j] for (i,j) in M.Arcs if j == k)
#     FlowOut = sum(M.x[i,j] for (i,j) in M.Arcs if i == l)
#     return FlowIn - FlowOut == 0
# model.BalanceEndLocations = Constraint(model.EndOfDayBridgeArcs, rule=end_of_day_locations)

# Create a problem instance
# Add appropriate data file 
instance = model.create_instance(datafile)
   
# Indicate which solver to use
Opt = SolverFactory("glpk")

# Generate a solution
Soln = Opt.solve(instance)

# Load solution to instance then Display the solution
instance.solutions.load_from(Soln)
display(instance)