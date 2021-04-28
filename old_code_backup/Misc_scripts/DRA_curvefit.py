import numpy as np
from hyperopt import hp, tpe, fmin, Trials


def objective(args):
    a = args['a']
    b = args['b']
    c = args['c']
    d = args['d']
    v = np.arange(0.5, 3, 0.1)
    vi = np.arange(0.5, 3, 0.1)*1e-6
    m = np.arange(0.1, 3, 0.1)
    a1 = 0.1
    b1 = 0.2
    c1 = 0.3
    d1 = 0.4

    error = 0
    for i in range(len(v)):
        f1 = (((c1 * v[i] * m[i]) ** 0.25) / ((d1 * vi[i]) ** 0.5) - a1) / (b1 - a1)
        f = (((c * v[i] * m[i]) ** 0.25) / ((d * vi[i]) ** 0.5) - a) / (b - a)
        error = error+abs(f1-f)
    return error


# Create the domain space
space = {'a': hp.uniform('a', 0, 0.2),
         'b': hp.uniform('b', 0, 0.3),
         'c': hp.uniform('c', 0, 0.4),
         'd': hp.uniform('d', 0, 0.5)}

# Create the algorithm
tpe_algo = tpe.suggest
# Create a trials object
tpe_trials = Trials()

# Run 2000 evals with the tpe algorithm
tpe_best = fmin(fn=objective, space=space,
                algo=tpe_algo, trials=tpe_trials,
                max_evals=3000)

print(tpe_best)
