import numpy as np
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator

import matplotlib.pyplot as plt
import io
import base64

COMPRESSED_HISTOGRAMS = 'distributions'
HISTOGRAMS = 'histograms'
IMAGES = 'images'
AUDIO = 'audio'
SCALARS = 'scalars'
TENSORS = 'tensors'
GRAPH = 'graph'
META_GRAPH = 'meta_graph'
RUN_METADATA = 'run_metadata'

DEFAULT_SIZE_GUIDANCE = {
    COMPRESSED_HISTOGRAMS: 0,
    IMAGES: 1,
    AUDIO: 0,
    SCALARS: 10000,
    HISTOGRAMS: 0,
    TENSORS: 0,
}

def is_outlier(points, thresh=3.5):
    """
    Returns a boolean array with True if points are outliers and False
    otherwise.

    Parameters:
    -----------
        points : An numobservations by numdimensions array of observations
        thresh : The modified z-score to use as a threshold. Observations with
            a modified z-score (based on the median absolute deviation) greater
            than this value will be classified as outliers.

    Returns:
    --------
        mask : A numobservations-length boolean array.

    References:
    ----------
        Boris Iglewicz and David Hoaglin (1993), "Volume 16: How to Detect and
        Handle Outliers", The ASQC Basic References in Quality Control:
        Statistical Techniques, Edward F. Mykytka, Ph.D., Editor.
    """
    if len(points.shape) == 1:
        points = points[:,None]
    median = np.median(points, axis=0)
    diff = np.sum((points - median)**2, axis=-1)
    diff = np.sqrt(diff)
    med_abs_deviation = np.median(diff)

    modified_z_score = 0.6745 * diff / med_abs_deviation

    return modified_z_score > thresh

class Report(object):
    def __init__(self,path,size_guidance=None):
        self._size_guidance =  size_guidance or DEFAULT_SIZE_GUIDANCE
        self.event_acc = EventAccumulator(path, self._size_guidance)

    def generate(self):
        self.event_acc.Reload()
        tags = self.event_acc.Tags()
        images = tags.get(IMAGES,[])
        scalars = tags.get(SCALARS,[])
        graphs = []
        for s in scalars:
            img = self.plot_scalar(s)
            graphs.append('<figure><img src="data:image/png;base64,{}"/></figure>'.format(img))
        graphs.append('<br/>')
        for i in images:
            img = self.plot_image(i)
            graphs.append('<figure><img src="data:image/png;base64,{}"/><figcaption>{}</figcaption></figure>'.format(img,i))
        return '<html>{}</html>'.format('\n'.join(graphs))

    def plot_image(self,name):
        data = self.event_acc.Images(name)[-1]
        return base64.b64encode(data.encoded_image_string).decode()

    def plot_scalar(self,name):
        plots = self.event_acc.Scalars(name)
        steps = len(plots)
        x = np.arange(steps)
        y = np.zeros([steps, 1])
        for i in range(steps):
            y[i, 0] = plots[i].value # value
            x[i] = plots[i].step # step

        good = ~is_outlier(y[:,0])
        y = y[good,:]
        x = x[good]
        plt.plot(x, y[:,0], label='train')

        plt.xlabel('Steps')
        plt.ylabel('Value')
        plt.title(name)
        plt.legend(loc='upper right', frameon=True)
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()
        return base64.b64encode(buf.getvalue()).decode()