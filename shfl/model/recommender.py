import abc
import numpy as np

from shfl.model.model import TrainableModel


class Recommender(TrainableModel):
    """
    Abstract class for recommender systems using \
        [TrainableModel](../model/#trainablemodel-class)
    """

    def __init__(self):
        self._clientId = None

    def train(self, data, labels):
        """
        Method that trains the model

        # Arguments:
            data: Data to train the model
            labels: Label for each train element
        """
        self._check_data(data)
        self._check_data_labels(data, labels)
        self._clientId = data[0, 0]
        self.train_recommender(data, labels)

    @abc.abstractmethod
    def train_recommender(self, data, labels):
        """
        Method that trains the model

        # Arguments:
            data: Data to train the model
            labels: Label for each train element
        """

    def predict(self, data):
        """
        Predict labels for data

        # Arguments:
            data: Data for predictions. Only includes the data of this client

        # Returns:
            predictions: Matrix with predictions for data
        """
        self._check_data(data)
        return self.predict_recommender(data)

    @abc.abstractmethod
    def predict_recommender(self, data):
        """
        Predict labels for data

        # Arguments:
            data: Data for predictions. Only includes the data of this client

        # Returns:
            predictions: Matrix with predictions for data
        """

    def evaluate(self, data, labels):
        """
        This method must return the performance in terms of different metrics of the prediction for those labels

        # Arguments:
            data: Data to be evaluated. Only includes the data of this client
            labels: True values of data
        """
        self._check_data(data)
        self._check_data_labels(data, labels)
        return self.evaluate_recommender(data, labels)

    @abc.abstractmethod
    def evaluate_recommender(self, data, labels):
        """
        This method must return the performance in terms of different metrics of the prediction for those labels

        # Arguments:
            data: Data to be evaluated. Only includes the data of this client
            labels: True values of data
        """

    @abc.abstractmethod
    def get_model_params(self):
        """
        Gets the params that define the model

        # Returns:
            params: Parameters defining the model
        """

    @abc.abstractmethod
    def set_model_params(self, params):
        """
        Update the params that define the model

        # Arguments:
            params: Parameters defining the model
        """

    def performance(self, data, labels):
        """
        This method must return the performance of the prediction in terms of the most representative metric
        for those labels.

        # Arguments:
            data: Data to be evaluated. Only includes the data of this client
            labels: True values of data
        """
        self._check_data(data)
        self._check_data_labels(data, labels)
        return self.performance_recommender(data, labels)

    @abc.abstractmethod
    def performance_recommender(self, data, labels):
        """
        This method must return the performance of the prediction in terms of the most representative metric
        for those labels.

        # Arguments:
            data: Data to be evaluated. Only includes the data of this client
            labels: True values of data
        """

    def _check_data(self, data):
        """
        Method that checks if the data corresponds to a single user

        # Arguments:
            data: array with data
        """
        number_of_clients = len(np.unique(data[:, 0]))
        print(number_of_clients)

        if number_of_clients > 1:
            raise AssertionError("Data need to correspond to a single user. "
                                 "Current data includes {} clients".format(number_of_clients))

    def _check_data_labels(self, data, labels):
        """
        Method that checks if the data and the labels have matching dimensions

        # Arguments:
            data: array with data
        """
        rows_in_data = data.shape[0]
        number_of_labels = len(labels)

        if rows_in_data != number_of_labels:
            raise AssertionError("Data and labels do not have matching dimensions. "
                                 "Current data has {} rows and there are {} labels".format(rows_in_data,
                                                                                           number_of_labels))
