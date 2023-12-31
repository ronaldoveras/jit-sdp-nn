# coding=utf-8
import jitsdp.constants as const

import numpy as np
import pandas as pd
from scipy.stats import mstats
from sklearn import metrics as met
import torch


def loss(df_prediction):
    return met.log_loss(df_prediction['target'], df_prediction['probability'])


def gmean(df_prediction):
    recall_1 = met.recall_score(
        df_prediction['target'], df_prediction['prediction'])
    return mstats.gmean([1. - recall_1, recall_1])


def __recalls(targets, predictions):
    classes = np.unique(targets)
    n_classes = len(classes)
    recalls = np.zeros(const.N_CLASSES)
    if n_classes == 0:
        return recalls
    confusion_matrix, _, _ = np.histogram2d(
        targets, predictions, bins=[n_classes, const.N_CLASSES])
    recalls[classes] = np.diag(confusion_matrix) / \
        np.sum(confusion_matrix, axis=1)
    return recalls


def __gmean(recalls):
    if np.isin(0.0, recalls):
        return 0.0
    return mstats.gmean(recalls)


def gmean_recalls(target_prediction):
    targets = target_prediction['target']
    predictions = target_prediction['prediction']
    recalls = __recalls(targets, predictions)
    return __gmean(recalls), recalls


def classifier_gmean_recalls(classifier, dataloader):
    if torch.cuda.is_available():
        classifier = classifier.cuda()

    with torch.no_grad():
        classifier.eval()
        recalls = np.zeros((const.N_CLASSES))
        for inputs, targets in dataloader:
            if torch.cuda.is_available():
                inputs, targets = inputs.cuda(), targets.cuda()

            outputs = classifier(inputs.float())
            predictions = torch.round(outputs).int()
            predictions = predictions.view(predictions.shape[0])
            recalls += __recalls(targets.detach().cpu().numpy(),
                                 predictions.detach().cpu().numpy())
        recalls = recalls / len(dataloader)
        return __gmean(recalls), recalls


def classifier_gmean(classifier, dataloader):
    gmean, _ = classifier_gmean_recalls(classifier, dataloader)
    return gmean


def proportions(label):
    total = len(label)
    p_normal = np.sum(label == 0) / total
    p_bug = 1.0 - p_normal
    return total, p_normal, p_bug


def prequential_recalls(results, fading_factor):
    recalls = []
    counts = np.zeros(const.N_CLASSES)
    hits = np.zeros(const.N_CLASSES)
    targets = results['target']
    predictions = results['prediction']
    n_samples = len(targets)
    for i in range(n_samples):
        label = targets[i]
        counts[label] = 1 + fading_factor * counts[label]
        hits[label] = int(label == predictions[i]) + \
            fading_factor * hits[label]
        recalls.append(hits / (counts + 1e-12))
    columns = ['r{}'.format(i) for i in range(const.N_CLASSES)]
    recalls = pd.DataFrame(recalls, columns=columns)
    return pd.concat([results, recalls], axis='columns')


def prequential_recalls_difference(recalls):
    recalls_difference = recalls.copy()
    recalls_difference['r0-r1'] = (recalls['r0'] - recalls['r1']).abs()
    return recalls_difference


def prequential_gmean(recalls):
    gmean = mstats.gmean(recalls[['r0', 'r1']], axis=1)
    gmean = pd.DataFrame(gmean, columns=['g-mean'])
    return pd.concat([recalls, gmean], axis='columns')


def prequential_proportions(results, fading_factor, threshold):
    proportions = []
    total = 0
    input_columns = ['target', 'prediction']
    counts = np.zeros(len(input_columns))
    values = results[input_columns].values
    n_samples = len(values)
    for i in range(n_samples):
        total = 1 + fading_factor * total
        counts = values[i] + fading_factor * counts
        proportions.append(counts / total)
    output_columns = ['te1', 'pr1']
    proportions = pd.DataFrame(proportions, columns=output_columns)
    proportions['th-ma'] = (threshold - results['ma']).abs()
    proportions['th-pr1'] = (threshold - proportions['pr1']).abs()
    return pd.concat([results, proportions], axis='columns')


def prequential_metrics(results, fading_factor, threshold):
    metrics = prequential_recalls(results, fading_factor)
    metrics = prequential_recalls_difference(metrics)
    metrics = prequential_gmean(metrics)
    return prequential_proportions(metrics, fading_factor, threshold)
