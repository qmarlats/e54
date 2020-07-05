class Forecaster:
    def forecast(self):
        # Fetch and prepare data
        self.fetch_data()
        self.prepare_data()

        # Initialize neural network
        nn = self.nn_class(evaluation_input=self.input_data)

        # Forecast
        nn.evaluate()

        return nn.evaluation_prediction
