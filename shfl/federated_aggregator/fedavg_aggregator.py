import numpy as np

from shfl.federated_aggregator.federated_aggregator import FederatedAggregator
from shfl.private.query import CheckDataType

class FedAvgAggregator(FederatedAggregator):
    """
    Implementation of Average Federated Aggregator. It only uses a simple average of the parameters of all the models.

    It implements [Federated Aggregator](../federated_aggregator/#federatedaggregator-class)
    """

    def aggregate_weights(self, clients_params):
        """
        Implementation of abstract method of class [AggregateWeightsFunction](../federated_aggregator/#federatedaggregator-class)
        # Arguments:
            clients_params: list of multi-dimensional (numeric) arrays. Each entry in the list contains the model's parameters of one client.

        # Returns
            aggregated_weights: aggregated weights representing the global learning model

        # References
            [Communication-Efficient Learning of Deep Networks from Decentralized Data](https://arxiv.org/abs/1602.05629)
        """

        aggregated_weights = [np.mean(np.array(params), axis=0) for params in zip(*clients_params)]
        
        is_scalar, is_array, is_list = CheckDataType().get(clients_params[0])
        if is_scalar or is_array: 
            aggragated_weights = aggragated_weights[0]
        
        return aggregated_weights
