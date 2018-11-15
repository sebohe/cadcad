from decimal import Decimal
import numpy as np
from fn.op import foldr

from SimCAD import Configuration, configs
from SimCAD.utils.configuration import exo_update_per_ts, proc_trigger, dict_elemwise_sum, bound_norm_random, \
    ep_time_step


seed = {
    'z': np.random.RandomState(1),
    'a': np.random.RandomState(2),
    'b': np.random.RandomState(3),
    'c': np.random.RandomState(3)
}

# Behaviors per Mechanism
# Different return types per mechanism ?? *** No ***
def b1m1(step, sL, s):
    return {'param1': 1}
def b2m1(step, sL, s):
    return {'param2': 4}

def b1m2(step, sL, s):
    return {'param1': 'a', 'param2': 2}
def b2m2(step, sL, s):
    return {'param1': 'b', 'param2': 4}

def b1m3(step, sL, s):
    return {'param1': ['c'], 'param2': np.array([10, 100])}
def b2m3(step, sL, s):
    return {'param1': ['d'], 'param2': np.array([20, 200])}


# Internal States per Mechanism
def s1m1(step, sL, s, _input):
    y = 's1'
    x = _input['param1']
    return (y, x)
def s2m1(step, sL, s, _input):
    y = 's2'
    x = _input['param2']
    return (y, x)

def s1m2(step, sL, s, _input):
    y = 's1'
    x = _input['param1']
    return (y, x)
def s2m2(step, sL, s, _input):
    y = 's2'
    x = _input['param2']
    return (y, x)

def s1m3(step, sL, s, _input):
    y = 's1'
    x = _input['param1']
    return (y, x)
def s2m3(step, sL, s, _input):
    y = 's2'
    x = _input['param2']
    return (y, x)

# Exogenous States
proc_one_coef_A = 0.7
proc_one_coef_B = 1.3

def es3p1(step, sL, s, _input):
    y = 's3'
    x = s['s3'] * bound_norm_random(seed['a'], proc_one_coef_A, proc_one_coef_B)
    return (y, x)

def es4p2(step, sL, s, _input):
    y = 's4'
    x = s['s4'] * bound_norm_random(seed['b'], proc_one_coef_A, proc_one_coef_B)
    return (y, x)

def es5p2(step, sL, s, _input): # accept timedelta instead of timedelta params
    y = 'timestamp'
    x = ep_time_step(s, s['timestamp'], seconds=1)
    return (y, x)


# Environment States
def env_a(x):
    return 10
def env_b(x):
    return 10
# def what_ever(x):
#     return x + 1

# Genesis States
state_dict = {
    's1': Decimal(0.0),
    's2': Decimal(0.0),
    's3': Decimal(1.0),
    's4': Decimal(1.0),
    'timestamp': '2018-10-01 15:16:24'
}

# remove `exo_update_per_ts` to update every ts
exogenous_states = exo_update_per_ts(
    {
    "s3": es3p1,
    "s4": es4p2,
    "timestamp": es5p2
    }
)

#	make env proc trigger field agnostic
env_processes = {
    "s3": proc_trigger('2018-10-01 15:16:25', env_a),
    "s4": proc_trigger('2018-10-01 15:16:25', env_b)
}

# lambdas
# genesis Sites should always be there
# [1, 2]
# behavior_ops = [ foldr(_ + _), lambda x: x + 0 ]


# [1, 2] = {'b1': ['a'], 'b2', [1]} =
# behavior_ops = [behavior_to_dict, print_fwd, sum_dict_values]
behavior_ops = [foldr(dict_elemwise_sum())]
# behavior_ops = []

# need at least 1 behaviour and 1 state function for the 1st mech with behaviors
# mechanisms = {}
mechanisms = {
    "m1": {
        "behaviors": {
            "b1": b1m1, # lambda step, sL, s: s['s1'] + 1,
            "b2": b2m1
        },
        "states": { # exclude only. TypeError: reduce() of empty sequence with no initial value
            "s1": s1m1,
            # "s2": s2m1
        }
    },
    "m2": {
        "behaviors": {
            "b1": b1m2,
            "b2": b2m2
        },
        "states": {
            "s1": s1m2,
            # "s2": s2m2
        }
    },
    "m3": {
        "behaviors": {
            "b1": b1m3,
            "b2": b2m3
        },
        "states": {
            "s1": s1m3,
            "s2": s2m3
        }
    }
}

sim_config = {
    "N": 2,
    "T": range(5)
}

configs.append(Configuration(sim_config, state_dict, seed, exogenous_states, env_processes, behavior_ops, mechanisms))