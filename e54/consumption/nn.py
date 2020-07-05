import torch

from core.nn import NN


class ConsumptionInFranceNN(NN):
    # Neural network information
    input_size = 12
    output_size = 1
    hidden_size = 20
    epochs = 500
    initial_learning_rate = 1e-3

    # Model
    model = torch.nn.Sequential(
        torch.nn.Linear(input_size, hidden_size),
        torch.nn.ReLU(),
        torch.nn.Linear(hidden_size, output_size),
    )
    state_dictionary_path = "consumption/media/consumption/consumptioninfrance.pth"
