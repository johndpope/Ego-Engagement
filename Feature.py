#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import numpy as np
import scipy.ndimage.filters as Filters

def read_gridflow(root):
    gridx = 16
    gridy = 12
    gridflow_path = os.path.join(root, "gridflow_{0}x{1}.txt".format(gridx, gridy))

    gridflows = []
    with open(gridflow_path, 'r') as fin:
        for line in fin:
            line = line.rstrip().split()
            gridflow = map(float,line[1:])
            gridflows.append(gridflow)
    gridflows = np.array(gridflows)
    return gridflows

def compute_avgflow(root):
    gridflows = read_gridflow(root)

    sigma = 30.0
    smoothed_flow = Filters.gaussian_filter1d(gridflows, sigma, axis=0, mode='nearest')

    sample_rate = 15
    smoothed_flow = smoothed_flow[::sample_rate,:]

    nsample, flow_length = smoothed_flow.shape
    feature_length = flow_length + 4

    features = np.zeros((nsample, feature_length))
    features[:,4:] = smoothed_flow

    smoothed_flow = smoothed_flow.reshape((nsample, -1, 2))
    flow_mean = np.mean(smoothed_flow, axis=1)
    flow_std = np.std(smoothed_flow, axis=1)
    features[:,0:2] = flow_mean
    features[:,2:4] = flow_std
    return features

def generate_proposals(confidence):
    n_threshold = 10
    scores = np.sort(confidence)
    samples = scores.shape[0] * np.arange(1, n_threshold+1) / (n_threshold + 1)
    thresholds = scores[samples]

    proposals = []
    for threshold in thresholds:
        start = 0
        cur_label = 1 if confidence[0] > threshold else 0
        for i in xrange(1, confidence.shape[0]):
            label = 1 if confidence[i] > threshold else 0
            if label != cur_label:
                proposal = (start, i)
                proposals.append(proposal)
                start = i
                cur_label = label
        proposal = (start, i)
        proposals.append(proposal)
    return proposals

def compute_TPM(proposals, features):
    pyramids = []
    for proposal in proposals:
        start, end = proposal
        seg = features[start:end,:]
        seg_length = seg.shape[0]

        pyramid_level = 3
        pyramid = []
        for level in xrange(pyramid_level):
            n_win = 2 ** level
            w_size = (seg_length - 1) / n_win + 1
            for i in xrange(n_win):
                s = min(i * w_size, seg_length-1)
                e = s + w_size
                w = seg[s:e,:]
                w_mean = np.mean(w, axis=0)
                w_std = np.std(w, axis=0)
                pyramid.append(w_mean)
                pyramid.append(w_std)
        pyramid = np.concatenate(pyramid)
        pyramids.append(pyramid)
    pyramids = np.vstack(pyramids)
    return pyramids

