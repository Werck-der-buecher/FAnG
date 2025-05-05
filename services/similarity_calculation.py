import sklearn.cluster
from skimage.color import rgba2rgb, rgb2gray
from skimage.transform import rescale
from skimage.util import invert
from typing import List
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

import time
import hdbscan
import numpy as np
import faiss

from services import Settings


def crop_invert_img(img: np.ndarray, crop: int):
    if img.shape[-1] in [4, 2]:
        img[..., -1] = 255
        img = rgba2rgb(img)
    if img.shape[-1] == 3:
        img = rgb2gray(img)
    img = invert(img)
    H, W = img.shape
    img = img[crop:H - crop, crop:W - crop]
    return img


def rescale_img(img: np.ndarray, scale: int, order: int = 1, anti_aliasing: bool = False):
    if img.shape[0] != 0 and img.shape[1] != 0:
        img = rescale(img, scale=scale, order=order, anti_aliasing=anti_aliasing)
    return img


def to_shape(a, shape):
    if 0 in a.shape:
        return np.zeros(shape, dtype=np.float32)

    a = a[:shape[0], :shape[1]]
    y_, x_ = shape[:2]
    y, x = a.shape[:2]
    y_pad = (y_ - y)
    x_pad = (x_ - x)

    cval = np.median(a)
    if a.ndim == 3:
        return np.pad(a, ((y_pad // 2, y_pad // 2 + y_pad % 2),
                          (x_pad // 2, x_pad // 2 + x_pad % 2),
                          (0, 0)),
                      mode='constant', constant_values=cval)
    else:
        return np.pad(a, ((y_pad // 2, y_pad // 2 + y_pad % 2),
                          (x_pad // 2, x_pad // 2 + x_pad % 2)),
                      mode='constant', constant_values=cval)


class SimilarityCalculationService(object):
    def preprocess_images(self, images, crop=6):
        # 1) Crop
        images = [crop_invert_img(img, crop=crop) for img in images]

        for img in images:
            if np.isnan(img).any():
                print("Crop")

        if not len(images):
            return None

        shapes = [d.shape for d in images]
        percentile_shape = np.percentile(shapes, 80, axis=0).astype(int)
        reference_shape = np.array([53, 49])  # 80th percentile shape
        enclosing_shape = np.array([59, 78])  # max shape

        # 2) Rescale
        shape_factor = (reference_shape - crop) / (percentile_shape - crop)
        scale = min(shape_factor) if np.mean(shape_factor) > 1 else max(shape_factor)

        images = [rescale_img(img, scale=scale) for img in images]

        for img in images:
            if np.isnan(img).any():
                print("Rescale")

        # 3) Homogenize shape via padding
        images = [to_shape(img, shape=enclosing_shape) for img in images]

        for img in images:
            if np.isnan(img).any():
                print("ToShape")

        return np.array(images)

    def pca(self, X: list[np.ndarray], num_comps: int = 128):
        X_flat = []
        for i, x in enumerate(X):
            X_flat.append(x.flatten())

        X_std = StandardScaler().fit_transform(X_flat)
        X_lowd = PCA(n_components=min(num_comps, len(X_flat), len(X_flat[0])),
                     svd_solver="randomized").fit_transform(X_std)
        return X_lowd

    def nearest_neighbour(self, X: list[np.ndarray]) -> List[int]:
        X_flat = []
        nan_indexes = []
        for i, x in enumerate(X):
            if np.isnan(x).any():
                nan_indexes.append(i)
                continue
            else:
                X_flat.append(x.flatten())

        # Scaling
        start = time.time()
        X_std = StandardScaler().fit_transform(X_flat)
        print("Scaling: ", time.time() - start)

        ncentroids = 16
        niter = 20
        verbose = True
        d = X_std.shape[1]
        kmeans = faiss.Kmeans(d, ncentroids, niter=niter, verbose=verbose)
        kmeans.train(X_std)

        D, I = kmeans.index.search(X_std, 1)
        sim_labels = I

        return sim_labels

    def hdbscan(self, X: list[np.ndarray], min_samples: int = 10) -> List[int]:
        X_flat = []
        nan_indexes = []
        for i, x in enumerate(X):
            if np.isnan(x).any():
                nan_indexes.append(i)
                continue
            else:
                X_flat.append(x.flatten())

        sim_labels = hdbscan.HDBSCAN(algorithm="prims_kdtree", min_samples=min_samples,
                                     min_cluster_size=50, core_dist_n_jobs=1).fit_predict(X_flat)
        sim_labels: List[int] = sim_labels.tolist()

        if max(sim_labels) == -1:
            sim_labels = [0] * len(sim_labels)

        for nidx in nan_indexes:
            sim_labels.insert(nidx, -1)

        return sim_labels

    def pca_hdbscan(self, X: List[np.ndarray], num_pca_comps: int = 8, min_samples: int = 10) -> List[int]:
        if len(X) < min_samples:
            return [-1 for _ in range(len(X))]

        X_flat = []
        nan_indexes = []

        values, counts = np.unique([x.shape[0] for x in X], return_counts=True)
        idx = np.argmax(counts)
        embd_dim = values[idx]
        for i, x in enumerate(X):
            if np.isnan(x).any() or x.shape[0] != embd_dim:
                nan_indexes.append(i)
                continue
            else:
                X_flat.append(x.flatten())

        # PCA
        X_std = StandardScaler().fit_transform(X_flat)
        pca = PCA(n_components=min(num_pca_comps, len(X_std), len(X_std[0])), svd_solver="randomized").fit(X_std)
        X_lowd = pca.transform(X_std)

        # HDBSCAN
        idx = np.random.choice(len(X_lowd), min(4000, len(X_lowd)), replace=False)
        clusterer = hdbscan.HDBSCAN(algorithm="boruvka_kdtree", min_samples=min_samples,
                                    core_dist_n_jobs=1, prediction_data=True).fit(X_lowd[idx, :])
        sim_labels, _ = hdbscan.approximate_predict(clusterer, X_lowd)
        sim_labels: List[int] = sim_labels.tolist()

        if max(sim_labels) == -1:
            sim_labels = [0] * len(sim_labels)

        for nidx in nan_indexes:
            sim_labels.insert(nidx, -1)

        return sim_labels

    def faiss(self, X: List[np.ndarray]) -> List[int]:
        X_flat = []
        nan_indexes = []

        values, counts = np.unique([x.shape[0] for x in X], return_counts=True)
        idx = np.argmax(counts)
        embd_dim = values[idx]
        for i, x in enumerate(X):
            if np.isnan(x).any() or x.shape[0] != embd_dim:
                nan_indexes.append(i)
                continue
            else:
                X_flat.append(x.flatten())

        X_std = StandardScaler().fit_transform(X_flat)

        # mat = faiss.PCAMatrix(3136, 16)
        # mat.train(X_std)
        # assert mat.is_trained
        # X_lowd = mat.apply(X_std)

        ncentroids = 16
        niter = 40
        d = X_std.shape[1]
        kmeans = faiss.Kmeans(d, ncentroids, niter=niter, verbose=False)
        kmeans.train(X_std)

        D, I = kmeans.index.search(X_std, 1)
        sim_labels: List[int] = I.squeeze().tolist()

        if max(sim_labels) == -1:
            sim_labels = [0] * len(sim_labels)

        for nidx in nan_indexes:
            sim_labels.insert(nidx, -1)

        return sim_labels
