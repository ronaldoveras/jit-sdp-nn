from jitsdp import plot

from constants import DIR

import numpy as np
import pandas as pd


def test_plot_recalls_gmean():
    config = {
        'dataset': 'brackets'
    }
    data = pd.DataFrame({
        'timestep': [0, 1, 2],
        'r0':    [0., 1., 2.],
        'r1':    [1., 0., 8.],
        'r0-r1': [1., 1., 6.],
        'gmean': [0., 0., 4.],
    })
    plot.plot_recalls_gmean(data=data, config=config, dir=DIR)
    assert (DIR / config['dataset'] / 'recalls_gmean.png').exists()


def test_plot_proportions():
    config = {
        'dataset': 'brackets'
    }
    data = pd.DataFrame({
        'timestep': [0, 1, 2],
        'p0':    [1., .5, 1.],
        'p1':    [0., .5, 0.],
    })
    plot.plot_proportions(data=data, config=config, dir=DIR)
    assert (DIR / config['dataset'] / 'proportions.png').exists()
