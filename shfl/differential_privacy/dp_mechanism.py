import numpy as np
import scipy

from shfl.private.data import DataAccessDefinition


class RandomizedResponseCoins(DataAccessDefinition):
    """
    This class uses a simple mechanism to add randomness for binary data. This algorithm is described
    by Cynthia Dwork and Aaron Roth in their work "The algorithmic Foundations of Differential Privacy".

    1.- Flip a coin

    2.- If tails, then respond truthfully.

    3.- If heads, then flip a second coin and respond "Yes" if heads and "No" if tails.

    # Arguments
        prob_head_first: float in [0,1] representing probability to use a random response instead of true value.
            This is equivalent to prob_head of the first coin flip algorithm described by Dwork.
        prob_head_second: float in [0,1] representing probability of respond true when random answer is provided.
            Equivalent to prob_head in the second coin flip in the algorithm.

    # References
        - [The algorithmic foundations of differential privacy](
           https://www.cis.upenn.edu/~aaroth/Papers/privacybook.pdf)
    """
    def __init__(self, prob_head_first=0.5, prob_head_second=0.5):
        self._prob_head_first = prob_head_first
        self._prob_head_second = prob_head_second

    def apply(self, data):
        """
        Implements the two coin flip algorithm described by Dwork.
        """
        _check_binary_data(data)
        size = _get_data_size(data)

        first_coin_flip = np.random.rand(size) > self._prob_head_first
        second_coin_flip = np.random.rand(size) < self._prob_head_second

        result = data * first_coin_flip + (1 - first_coin_flip) * second_coin_flip

        if np.isscalar(data):
            result = int(result)

        return result


class RandomizedResponseBinary(DataAccessDefinition):
    """
    Implements the most general binary randomized response algorithm. Both the input and output are binary
    arrays or scalars. The algorithm is defined through the conditional probabilities

    - P( output=0 | input=0 ) = f0
    - P( output=1 | input=1) = f1

    For f0=f1=0 or 1, the algorithm is not random. It is maximally random for f0=f1=1/2.
    This class contains, for special cases of f0, f1, the class RandomizedResponseCoins.

    # Arguments
        f0: float in [0,1] representing the probability of getting 0 when the input is 0
        f1: float in [0,1] representing the probability of getting 1 when the input is 1
    """

    def __init__(self, f0, f1):
        self._f0 = f0
        self._f1 = f1

    def apply(self, data):
        """
        Implements the general binary randomized response algorithm.

        Both the input and output of the method are binary arrays.
        """
        _check_binary_data(data)
        size = _get_data_size(data)

        if size > 1:
            # Binary array case
            x_response = np.zeros(size)
            x_zero = data == 0
            x_response[x_zero] = scipy.stats.bernoulli.rvs(1 - self._f0, size=sum(x_zero))
            x_response[~x_zero] = scipy.stats.bernoulli.rvs(self._f1, size=len(data)-sum(x_zero))
        else:
            # Scalar case
            if data == 0:
                x_response = int(scipy.stats.bernoulli.rvs(1 - self._f0, size=1))
            else:
                x_response = int(scipy.stats.bernoulli.rvs(self._f1, size=1))

        return x_response


class LaplaceMechanism(DataAccessDefinition):
    """
    Implements the laplace mechanism for differential privacy defined by Dwork in their work
    "The algorithmic Foundations of Differential Privacy".

    Notice that the Laplace mechanism is a randomization algorithm that depends on the sensitivity,
    which can be regarded as a numeric query. One can show that this mechanism is
    epsilon-differentially private with epsilon = sensitivity/b where b is a constant.

    In order to apply this mechanism for a particular value of epsilon, we need to compute
    the sensitivity, which might be hard to compute in practice. The framework provides
    a method to estimate the sensitivity of a query that maps the private data in a normed space
    (see: [SensitivitySampler](../Sensitivity Sampler))

    # Arguments:
        query: Function to apply over private data (see: [Query](../../Query))
        sensitivity: float representing sensitivity of the applied query
        epsilon: float for the epsilon you want to apply

    # References
        - [The algorithmic foundations of differential privacy](
           https://www.cis.upenn.edu/~aaroth/Papers/privacybook.pdf)
    """
    def __init__(self, query, sensitivity, epsilon):
        self._query = query
        self._sensitivity = sensitivity
        self._epsilon = epsilon

    def apply(self, data):
        query_result = self._query.get(data)
        size = _get_data_size(query_result)
        b = self._sensitivity/self._epsilon

        return data + np.random.laplace(loc=0.0, scale=b, size=size)


def _get_data_size(data):
    if np.isscalar(data):
        size = 1
    else:
        size = len(data)

    return size


def _check_binary_data(data):
    if np.isscalar(data):
        if data != 0 and data != 1:
            raise ValueError("Randomized mechanism works with binary scalars, but input is not binary")
    elif not np.array_equal(data, data.astype(bool)):
        raise ValueError("Randomized mechanism works with binary data, but input is not binary")
