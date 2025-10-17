import torch
import torch.nn as nn


def main():
    """
    Initializes a simple linear model, generates a random input tensor,
    and prints the model's output.
    """
    print("--- ML Model Execution Start ---")

    # Define model parameters
    # The model will take an input of size 10 and produce an output of size 5.
    in_features = 10
    out_features = 5

    # Instantiate the model: a single linear layer
    # This is one of the simplest neural network layers possible.
    model = nn.Linear(in_features, out_features)
    print(f"Model initialized: {model}")

    # Create a dummy input tensor
    # The input tensor must have a shape compatible with the model's in_features.
    # Here, we create a single sample (batch size of 1).
    # Shape: [batch_size, in_features]
    input_tensor = torch.randn(1, in_features)
    print(f"\nGenerated random input tensor with shape: {input_tensor.shape}")

    # Set the model to evaluation mode
    # This is a best practice, though it has little effect on a simple linear layer.
    model.eval()

    # Perform inference
    # We use torch.no_grad() to disable gradient calculations, which is more
    # memory-efficient and faster for pure inference tasks.
    with torch.no_grad():
        output = model(input_tensor)

    print(f"Model produced output tensor with shape: {output.shape}")
    print(f"Output tensor:\n{output}")
    print("\n--- ML Model Execution Complete ---")
    return output

