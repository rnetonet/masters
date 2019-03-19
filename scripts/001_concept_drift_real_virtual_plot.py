import matplotlib.pyplot as plt
import numpy as np
from sklearn.datasets.samples_generator import make_blobs

X, _ = make_blobs(n_samples=300, centers=4, cluster_std=0.30, random_state=0)

f, ((ax1, ax2, ax3)) = plt.subplots(1, 3, sharey=True)


ax1.scatter(X[:, 0], X[:, 1], "o", color="red")
# ax1.scatter(X[:, 2], X[:, 3], "o", color="blue")

ax1.set_title("Dados Originais")

# ax2.scatter(ax, ay)
# ax3.scatter(ax, ay)


plt.show()
