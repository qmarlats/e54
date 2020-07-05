import numpy as np
import pandas as pd
import torch


class NN:
    def __init__(
        self,
        evaluation_input,
        evaluation_output=None,
        training_input=None,
        training_output=None,
        device="cpu",
    ):
        # Data
        # Note: we do NOT prefix these variables with an underscore
        # in order to initialize them using their setters, hence
        # ensuring their data type
        self.evaluation_input = evaluation_input
        self.evaluation_output = evaluation_output
        self.training_input = training_input
        self.training_output = training_output

        # Device
        # Note: we do NOT prefix this variable with an underscore
        # in order to initialize it using its setter, hence ensuring
        # its data type
        self.device = device

    @property
    def evaluation_input(self):
        return self._evaluation_input

    @evaluation_input.setter
    def evaluation_input(self, value):
        if isinstance(value, pd.DataFrame):
            self._evaluation_input = value.values.astype(np.float64)
        else:
            self._evaluation_input = value

    @property
    def evaluation_output(self):
        return self._evaluation_output

    @evaluation_output.setter
    def evaluation_output(self, value):
        if isinstance(value, pd.DataFrame):
            self._evaluation_output = value.values.astype(np.float64)
        else:
            self._evaluation_output = value

    @property
    def training_input(self):
        return self._training_input

    @training_input.setter
    def training_input(self, value):
        if isinstance(value, pd.DataFrame):
            self._training_input = value.values.astype(np.float64)
        else:
            self._training_input = value

    @property
    def training_output(self):
        return self._training_output

    @training_output.setter
    def training_output(self, value):
        if isinstance(value, pd.DataFrame):
            self._training_output = value.values.astype(np.float64)
        else:
            self._training_output = value

    @property
    def device(self):
        return self._device

    @device.setter
    def device(self, value):
        if isinstance(value, str):
            self._device = torch.device(value)
        else:
            self._device = value

        # Update model
        self.model.to(self.device)

    @staticmethod
    def ape(output, predicted):
        return 100 * np.abs((output - predicted) / output)

    @staticmethod
    def mape(output, predicted):
        # We need to split this calculation to handle properly
        # the cases where output is 0 (hence division by 0),
        # which happends when forecasting renewable sources
        with np.errstate(divide="ignore", invalid="ignore"):
            div = (output - predicted) / output
            div[div == np.inf] = 0
            div[div == -np.inf] = 0
            div = np.nan_to_num(div)
            mape = 100 / output.shape[0] * np.sum(np.abs(div))

        return mape

    def train(self):
        # Set model in train mode
        model = self.model.train()

        # Tensors
        training_input_tensor = torch.tensor(
            self.training_input, dtype=torch.float, device=self.device
        )
        training_output_tensor = torch.tensor(
            self.training_output, dtype=torch.float, device=self.device
        )

        # Define the optimizer, the scheduler and the loss function:
        #  - The optimizer will update the model parameters using the
        #    choosen algorithm
        #  - The scheduler will update the learning rate dynamically
        #  - The loss function will calculte the error between the
        #    prediction and the real data
        optimizer = torch.optim.Adam(model.parameters(), lr=self.initial_learning_rate)
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer)
        loss_function = torch.nn.MSELoss(reduction="sum")

        # Initialize losses array
        losses = np.zeros(self.epochs)

        # Train model
        for epoch in range(self.epochs):
            # Predict output using the model
            predicted = model(training_input_tensor)

            # Compute and save loss
            loss = loss_function(predicted, training_output_tensor)
            losses[epoch] = loss.item()

            # Clear gradients
            optimizer.zero_grad()

            # Compute gradients
            loss.backward()

            # Update parameters
            optimizer.step()

            # Update scheduler
            scheduler.step(loss.item())

        # Run a final prediction using the final model parameters
        predicted = model(training_input_tensor)

        # Save model, losses and final prediction
        self.model = model
        self.training_losses = losses
        self.training_prediction = predicted.cpu().detach().numpy()

    def evaluate(self):
        # Set model in evaluation mode
        model = self.model.eval()

        # Load model state dictionnary if necessary
        if self.state_dictionary_path:
            model.load_state_dict(
                torch.load(self.state_dictionary_path, map_location=self.device)
            )

        # Tensors
        evaluation_input_tensor = torch.tensor(
            self.evaluation_input, dtype=torch.float, device=self.device
        )

        # Predict output using the model
        predicted = model(evaluation_input_tensor)

        # Save prediction
        self.evaluation_prediction = predicted.cpu().detach().numpy()

    def save_model(self, path):
        torch.save(self.model.state_dict(), path)

    def save_training_losses(self, path):
        pd.DataFrame(self.training_losses).to_csv(path, index=False)

    def save_training_prediction(self, path):
        pd.DataFrame(self.training_prediction).to_csv(path, index=False)

    def save_evaluation_prediction(self, path):
        pd.DataFrame(self.evaluation_prediction).to_csv(path, index=False)
