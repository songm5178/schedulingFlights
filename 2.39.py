# Pyomo Template

# These two lines are required.  DO NOT REMOVE

from __future__ import division
from pyomo.environ import *
from pyomo.opt import *

# indicate your data file name here

datafile = "2.39.dat"
# Instantiate the model

model = AbstractModel()
model.name = "Minimum Cost Network Flow Model"

# Define sets

# Nodes in the network
model.Nodes = Set()
# Network arcs
model.Arcs = Set(within=model.Nodes*model.Nodes)

# Define Parameters

# Cost per unit flow across each arc
model.c = Param(model.Arcs, within=NonNegativeReals)

# Upper bound on flow across each arc
model.u = Param(model.Arcs, within=NonNegativeReals)


# Flow balance through each node:
# Positive balance means more into node than outgoing
# Negative balance means more outgoing from node than coming into
# Zero balance means Flow in == Flow Out
# Should have Total Balance = 0

model.balance = Param(model.Nodes)

# Define Variables 

# The flow over each arc
model.x = Var(model.Arcs, within=NonNegativeReals)


## Define Objective
# Minimize the cost of the flow across the network
def TotalCost(M):
    return sum(M.c[i, j] * M.x[i,j] for (i, j) in M.Arcs)
    
model.total = Objective(rule=TotalCost, sense=minimize)


## Constraints

# Enforce an upper limit on the flow across each arc
def limit_rule(M, i, j):
    return M.x[i,j] <= M.u[i, j]
    
model.limit = Constraint(model.Arcs, rule=limit_rule)

# Enforce flow balance through each node
def flow_rule(M, k):
    FlowIn  = sum(M.x[i,j] for (i,j) in M.Arcs if j == k)
    FlowOut = sum(M.x[i,j] for (i,j) in M.Arcs if i == k)
    return FlowIn - FlowOut == M.balance[k]
    
model.FlowBalance = Constraint(model.Nodes, rule=flow_rule)


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