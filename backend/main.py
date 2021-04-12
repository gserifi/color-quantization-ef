from base64 import b64decode, b64encode
import numpy as np
from scipy.spatial.distance import cdist
from sklearn.decomposition import PCA
from io import BytesIO
from imageio import imread
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time
import random
from tqdm import trange

MAX_ITER = 100

def decode(image):
  decoded = b64decode(image)
  pixels = np.array(imread(BytesIO(decoded)))
  pixels = np.delete(pixels, 3, 1)

  return pixels

def k_means(k, points):
  cluster = np.random.randint(256, size=(k, 3))
  prev_dim = (points.shape[0], points.shape[1])
  points = np.reshape(points, (points.shape[0] * points.shape[1], 3))

  iter = 0
  for _ in trange(MAX_ITER):
    iter += 1
    distances = cdist(points, cluster)
    pointToCluster = np.argmin(distances, axis=1)

    next_cluster = np.empty((k, 3))
    for i in range(k):
      matches = points[pointToCluster == i]
      if not matches.shape[0]:
        matches = np.random.randint(256, size=(1, 3))
      next_cluster[i] = np.mean(matches.transpose(), axis=1)

    if np.array_equal(cluster, next_cluster):
      break
    cluster = next_cluster

  pointToCluster = np.reshape(pointToCluster, prev_dim)

  return cluster, pointToCluster, iter

with open("kolibri.jpg", "rb") as image_file:
  encoded_string = b64encode(image_file.read())
  pixels = decode(encoded_string)
  flat_pixels = np.reshape(pixels, (pixels.shape[0] * pixels.shape[1], 3))
  ground_truth = np.copy(pixels)
  flat_ground_truth = np.copy(flat_pixels)

  t0 = time.time()
  cluster, pointToCluster, iter = k_means(10, pixels)
  print("K-Means done in {:.3f} seconds within {} iterations!".format(time.time()-t0, iter))

  for i in range(pixels.shape[0]):
    for j in range(pixels.shape[1]):
      pixels[i, j] = cluster[pointToCluster[i, j]]

  f, sub = plt.subplots(2, 1)
  sub[0].imshow(ground_truth)
  sub[1].imshow(pixels)
  plt.show()

  pca = PCA(n_components=2)
  transformed_pixels = pca.fit_transform(flat_ground_truth)
  transformed_cluster = pca.transform(cluster)

  sample_indices = random.sample(list(range(transformed_pixels.shape[0])), k=2000)

  for sample_index in sample_indices:
    pixel = transformed_pixels[sample_index]
    ground_pixel = flat_ground_truth[sample_index]
    plt.scatter(pixel[0], pixel[1], marker="o", s=1, color=(ground_pixel[0] / 255,ground_pixel[1] / 255,ground_pixel[2] / 255))

  for i, transformed_c in enumerate(transformed_cluster):
    c = cluster[i]
    plt.scatter(transformed_c[0], transformed_c[1], marker="o", s=200, color=(c[0] / 255, c[1] / 255, c[2] / 255))

  plt.show()

  fig = plt.figure()
  ax = Axes3D(fig)

  for c in cluster:
    ax.scatter(c[0], c[1], c[2], marker="o", s=200, color=(c[0] / 255, c[1] / 255, c[2] / 255))

  sample_indices = random.sample(list(range(ground_truth.shape[0] * ground_truth.shape[1])), k=300)
  sample_space = np.reshape(ground_truth, (ground_truth.shape[0] * ground_truth.shape[1],3))
  for sample_index in sample_indices:
    pixel = sample_space[sample_index]
    ax.scatter(pixel[0], pixel[1], pixel[2], marker="o", s=1, color=(pixel[0] / 255, pixel[1] / 255, pixel[2] / 255))

  plt.show()