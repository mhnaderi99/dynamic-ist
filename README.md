# AdapTrain

<p align="center">
  <img src="./docs/adaptrain-logo.webp" alt="AdapTrain logo" width="40%" height="40%">
</p>
<p align="center" style="font-size: 11px;">
  [This logo is generated using DALL.E 3 by OpenAI]
</p>

AdapTrain is a framework designed to optimize distributed training in heterogeneous environments. AdapTrain handles workload variations and cloud multi-tenancy effectively, achieving up to 8.2× faster convergence compared to existing methods.

The key features of AdapTrain are:
- **Dynamic Model Partitioning:** Automatically adjusts model partitioning based on each worker's computational capacity to optimize resource utilization.
- **Reduced Synchronization Overhead:** Minimizes delays by ensuring synchronized completion of training rounds across all workers.
- **Robust to Variations:** Performs reliably under workload variations, resource heterogeneity, and cloud multi-tenancy.
- **Accelerated Model Convergence:** Demonstrates up to 8.2× faster convergence compared to state-of-the-art distributed training methods.


## Setup


## How to use?


We receive the nodes specefication to deploy the AdapTrain learning method on. These nodes are specified in deployment.yaml file.

Use PVC for dataset sharing between nodes.

Aggregate the common and shared layers of the model.

TODO:
    1. Implement Worker parameter model training and initialization.
    2. Implement Controller-worker communication.
    3. Dataset, deployment, kubernetes, and model configuration.