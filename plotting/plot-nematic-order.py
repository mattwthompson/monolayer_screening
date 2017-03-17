import os

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

import signac

# I feel like this could be grabbed from somewhere...
terminal_groups = ['cyano', 'cyclopropyl', 'nitro']
chainlengths = [6, 12, 18]

project = signac.get_project()

fig, ax = plt.subplots()

for terminal_group in terminal_groups:
    proto_s2 = []
    proto_s2_err = []
    for chainlength in chainlengths:
        local_s2 = []
        for job in project.find_jobs({'terminal_group': terminal_group, 
                                      'chainlength': chainlength}):
            s2_file = os.path.join(job.workspace(), 'nematic-order.txt')
            if os.path.isfile(s2_file):
                s2_traj = np.loadtxt(s2_file)
                s2_traj = s2_traj[int(len(s2_traj)*(3/4)):,1]
                local_s2.append(np.mean(s2_traj))
        proto_s2.append(np.mean(local_s2))
        proto_s2_err.append(np.std(local_s2))
    ax.errorbar(chainlengths, proto_s2, yerr=proto_s2_err, marker='o', 
        label=terminal_group)

plt.xlabel('Chain length, # of carbons')
plt.ylabel('Nematic order, S2')
plt.legend()
plt.tight_layout()
fig.savefig('nematic-order.pdf')
