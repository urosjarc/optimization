# import numpy as np
# import matplotlib.pyplot as plt
#
#
# from sklearn import decomposition
# from sklearn import datasets
#
# centers = [[1, 1], [-1, -1], [1, -1]]
# iris = datasets.load_iris()
# X = iris.data
# y = iris.target
#
# plt.cla()
# pca = decomposition.PCA(n_components=2)
# pca.fit(X)
# X = pca.transform(X)
# y = np.choose(y, [1, 2, 0]).astype(float)
# zz = np.array([[xi+yi for xi in X[:,0]] for yi in X[:,1]])
# plt.scatter(X[:, 0], X[:, 1])
#
# plt.show()