import torch
import torch.nn as nn

from src.configurations.defaults import LAYERS_TO_PARTITION

from typing import List


def adaptive_partitioning():
    pass


def partition_layer(layer: nn.Module,
                    partition_weights: bool,
                    partition_biases: bool,
                    partition_dim_0_indices = None,
                    partition_dim_1_indices = None):
    """_summary_

    Args:
        layer (nn.Module): Layer to partition.
        partition_weights (bool): Whether to partition weights.
        partition_biases (bool): Whether to partition biases.
        partition_dim_0_indices (List[int], optional): Indices to partition along dim 0.
        partition_dim_1_indices (List[int], optional): Indices to partition along dim 1.

    Returns:
        _type_: Partitions of the layer.
    """
    
    if not isinstance(layer, tuple(LAYERS_TO_PARTITION)):
        raise ValueError(f"Layer {layer} is not supported for partitioning.")
    
    
    weight_partitions = []
    bias_partitions = []
    
    if isinstance(layer, nn.Linear):
        weight_tensor = layer.weight
        bias_tensor = layer.bias if layer.bias is not None else None

        # Partition weights and biases along both dimensions
        if partition_dim_0_indices and partition_dim_1_indices:
            
            for i in range(len(partition_dim_0_indices)):
                if partition_weights:
                    temp_weight = torch.index_select(weight_tensor, 0, partition_dim_0_indices[i])  # Select rows (dim 0)
                    current_weight = torch.index_select(temp_weight, 1, partition_dim_1_indices[i])  # Select cols (dim 1)
                    weight_partitions.append(current_weight.clone())
                if partition_biases and bias_tensor is not None:
                    current_bias = torch.index_select(bias_tensor, 0, partition_dim_0_indices[i])  # Select rows (dim 0)
                    bias_partitions.append(current_bias.clone())

        # Partition weights and biases along dim 0 only
        elif partition_dim_0_indices:
            for curr_index in partition_dim_0_indices:
                if partition_weights:
                    current_weight = torch.index_select(weight_tensor, 0, curr_index)  # Select rows (dim 0)
                    weight_partitions.append(current_weight.clone())
                if partition_biases and bias_tensor is not None:
                    current_bias = torch.index_select(bias_tensor, 0, curr_index)  # Select rows (dim 0)
                    bias_partitions.append(current_bias.clone())

        # Partition weights along dim 1 only
        elif partition_dim_1_indices:
            for curr_index in partition_dim_1_indices:
                if partition_weights:
                    current_weight = torch.index_select(weight_tensor, 1, curr_index)  # Select cols (dim 1)
                    weight_partitions.append(current_weight.clone())
    
    elif isinstance(layer, nn.BatchNorm1d) and partition_dim_0_indices:
        for curr_index in partition_dim_0_indices:
            if partition_weights:
                current_weight_tensor = torch.index_select(layer.weight, 0, curr_index)
                weight_partitions.append(current_weight_tensor.clone())
            if partition_biases:
                current_bias_tensor = torch.index_select(layer.bias, 0, curr_index)
                bias_partitions.append(current_bias_tensor.clone())
                
                  
    return weight_partitions, bias_partitions


def update_layer(layer: nn.Module,
                 update_weights: List[torch.Tensor],
                 update_biases: List[torch.Tensor],
                 update_dim_0_indices=None,
                 update_dim_1_indices=None):
    """_summary_

    Args:
        layer (nn.Module): Layer to update.
        update_weights (List[torch.Tensor]): Weights to update.
        update_biases (List[torch.Tensor]): Biases to update.
        update_dim_0_indices (List[int], optional): Indices to update along dim 0.
        update_dim_1_indices (List[int], optional): Indices to update along dim 1.

    Returns:
        _type_: Updated layer.
    """
    
    if not isinstance(layer, tuple(LAYERS_TO_PARTITION)):
        raise ValueError(f"Layer {layer} is not supported for partitioning.")
    
    if isinstance(layer, nn.Linear):
        # Access weights and biases
        weight_tensor = layer.weight.clone()
        bias_tensor = layer.bias.clone() if layer.bias is not None else None

        # Update along both dimensions (dim 0 and dim 1)
        if update_dim_0_indices is not None and update_dim_1_indices is not None:
            for i in range(len(update_weights)):
                curr_index_0 = update_dim_0_indices[i]
                curr_index_1 = update_dim_1_indices[i]
                temp_tensor = torch.index_select(weight_tensor, 0, curr_index_0)
                temp_tensor.index_copy_(1, curr_index_1, update_weights[i])  # Update along dim 1
                weight_tensor.index_copy_(0, curr_index_0, temp_tensor)  # Update along dim 0

        # Update along dim 0 only (output dimension)
        elif update_dim_0_indices is not None:
            for i in range(len(update_weights)):
                curr_index = update_dim_0_indices[i]
                weight_tensor.index_copy_(0, curr_index, update_weights[i])  # Update weights
                if bias_tensor is not None and update_biases is not None:
                    bias_tensor.index_copy_(0, curr_index, update_biases[i])  # Update biases

        # Update along dim 1 only (input dimension)
        elif update_dim_1_indices is not None:
            for i in range(len(update_weights)):
                curr_index = update_dim_1_indices[i]
                weight_tensor.index_copy_(1, curr_index, update_weights[i])  # Update weights

    elif isinstance(layer, nn.BatchNorm1d):
        # Access weights and biases
        weight_tensor = layer.weight
        bias_tensor = layer.bias

        if update_dim_0_indices is not None:
            for i in range(len(update_weights)):
                curr_index = update_dim_0_indices[i]
                weight_tensor.index_copy_(0, curr_index, update_weights[i])  # Update weights
                if update_biases is not None:
                    bias_tensor.index_copy_(0, curr_index, update_biases[i])  # Update biases

    if update_weights is not None:
        layer.weight.data = weight_tensor
    
    if update_biases is not None:
        layer.bias.data = bias_tensor
    
    return layer