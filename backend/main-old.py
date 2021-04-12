from base64 import b64decode, b64encode
import numpy as np
from scipy.spatial.distance import cdist
from io import BytesIO
from imageio import imread
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time

MAX_ITER = 5

def decode(image):
  decoded = b64decode(image)
  pixels = np.array(imread(BytesIO(decoded)))
  pixels = np.delete(pixels, 3, 1)

  return pixels

def k_means(k, points):
  cluster = np.random.randint(256, size=(k, 3))
  points = np.reshape(points, (points.shape[0] * points.shape[1], 3))

  for _ in range(MAX_ITER):
    distances = cdist(points, cluster)
    pointToCluster = np.argmin(distances, axis=1)
    clusterToPoint = [[] for _ in range(k)]
    pointToCluster = {}
    for point in points:
      distances = np.linalg.norm(point - cluster, axis=1)
      nearest_index = np.argmin(distances)
      if not clusterToPoint[nearest_index]:
        clusterToPoint[nearest_index] = []
      clusterToPoint[nearest_index].append(list(point))
      pointToCluster[str(point)] = nearest_index

    for i in range(k):
      if not clusterToPoint[i]:
        clusterToPoint[i] = list(np.random.randint(256, size=(1,3)))
      cluster[i] = np.mean(
        np.array(
          clusterToPoint[i])
          .transpose()
          , axis=1)

  return cluster, pointToCluster

with open("colors.png", "rb") as image_file:
  encoded_string = b64encode(image_file.read())
  pixels = decode(encoded_string)
  ground_truth = np.copy(pixels)

  t0 = time.time()
  cluster, pointToCluster = k_means(7, pixels)
  print("K-Means done in {:.3f} seconds!".format(time.time()-t0))

  for i in range(pixels.shape[0]):
    for j in range(pixels.shape[1]):
      pixels[i, j] = cluster[pointToCluster[str(pixels[i, j])]]

  f, sub = plt.subplots(2, 1)
  sub[0].imshow(ground_truth)
  sub[1].imshow(pixels)
  plt.show()

  fig = plt.figure()
  ax = Axes3D(fig)

  for c in cluster:
    ax.scatter(c[0], c[1], c[2], marker="o", s=200, color=(c[0] / 255, c[1] / 255, c[2] / 255))

  count = 0
  for i in range(ground_truth.shape[0]):
    for j in range(ground_truth.shape[1]):
      if not count % 50:
        pixel = ground_truth[i, j]
        ax.scatter(pixel[0], pixel[1], pixel[2], marker="o", s=1, color=(pixel[0] / 255, pixel[1] / 255, pixel[2] / 255))
      count += 1

  plt.show()

  plt.show()