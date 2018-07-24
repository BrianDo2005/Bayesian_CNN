# Bayesian CNN

Implementation of [Bayes by Backprop](https://arxiv.org/abs/1505.05424) in a convolutional neural network.

### One convolutional layer with distributions over weights in each filter

![Distribution over weights in a CNN's filter.](figures/CNNwithdist.png)

### Fully Bayesian perspective of an entire CNN 

![Distributions must be over weights in convolutional layers and weights in fully-connected layers.](figures/CNNwithdist_git.png)

### Results 
#### Results on MNIST and CIFAR-10 with LeNet-5 and 3Conv3FC, respectively

![Results on MNIST and CIFAR-10 with LeNet-5 and 3Conv3FC, respectively](figures/results_CNN.png)

Please cite:
´´´
@article{laumann2018bayesian,
  title={Bayesian Convolutional Neural Networks},
  author={Laumann, Felix and Shridhar, Kumar},
  journal={arXiv preprint arXiv:1806.05978},
  year={2018}
}
´´´
