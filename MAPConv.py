import torch
import os
import torchvision.datasets as dsets
import torchvision.transforms as transforms
import torch.utils.data as data
import torch.nn as nn
import pickle
from MAPConvmodels import LeNet, _3Conv3FC, ELUN1, CNN1

cuda = torch.cuda.is_available()

'''
HYPERPARAMETERS
'''
is_training = True  # set to "False" to only run validation
net = CNN1
batch_size = 64
dataset = 'CIFAR-100'  # MNIST, CIFAR-10 or CIFAR-100
num_epochs = 100
lr = 0.00001
weight_decay = 0.0005

# dimensions of input and output
if dataset is 'MNIST':    # train with MNIST version
    outputs = 10
    inputs = 1
elif dataset is 'CIFAR-10':  # train with CIFAR-10
    outputs = 10
    inputs = 3
elif dataset is 'CIFAR-100':    # train with CIFAR-100
    outputs = 100
    inputs = 3
elif dataset is 'ImageNet':    # train with ImageNet
    outputs = 1000
    inputs = 3
else:
    pass

if net is LeNet:
    resize = 32
elif net is _3Conv3FC:
    resize = 32
elif net is ELUN1:
    resize = 32
elif net is CNN1:
    resize = 32
else:
    pass

'''
LOADING DATASET
'''

if dataset is 'MNIST':
    transform = transforms.Compose([transforms.Resize((resize, resize)), transforms.ToTensor(),
                                    transforms.Normalize((0.1307,), (0.3081,))])
    train_dataset = dsets.MNIST(root="data", download=True, transform=transform)
    val_dataset = dsets.MNIST(root="data", download=True, train=False, transform=transform)

elif dataset is 'CIFAR-100':
    transform = transforms.Compose([transforms.Resize((resize, resize)), transforms.ToTensor(),
                                    transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))])
    train_dataset = dsets.CIFAR100(root="data", download=True, transform=transform)
    val_dataset = dsets.CIFAR100(root='data', download=True, train=False, transform=transform)

elif dataset is 'CIFAR-10':
    transform = transforms.Compose([transforms.Resize((resize, resize)), transforms.ToTensor(),
                                    transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))])
    train_dataset = dsets.CIFAR10(root="data", download=True, transform=transform)
    val_dataset = dsets.CIFAR10(root='data', download=True, train=False, transform=transform)

elif dataset is 'ImageNet':
    transform = transforms.Compose([transforms.Resize((resize, resize)), transforms.ToTensor(),
                                    transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))])
    train_dataset = dsets.ImageFolder(root="data", transform=transform)
    val_dataset = dsets.ImageFolder(root='data', transform=transform)

'''
MAKING DATASET ITERABLE
'''

print('length of training dataset:', len(train_dataset))
n_iterations = num_epochs * (len(train_dataset) / batch_size)
n_iterations = int(n_iterations)
print('Number of iterations: ', n_iterations)

loader_train = data.DataLoader(dataset=train_dataset, batch_size=batch_size, shuffle=True)

loader_val = data.DataLoader(dataset=val_dataset, batch_size=batch_size, shuffle=False)


'''
INSTANTIATE MODEL
'''

model = net(outputs=outputs, inputs=inputs)

if cuda:
    model.cuda()

# Loss and optimizer
criterion = nn.CrossEntropyLoss()
optimiser = torch.optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=lr, weight_decay=weight_decay)

logfile = os.path.join('diagnostics_1.txt')
with open(logfile, 'w') as lf:
    lf.write('')


def run_epoch(loader):
    accuracies = []
    losses = []

    for i, (images, labels) in enumerate(loader):
        # Repeat samples (Casper's trick)
        x = images.view(-1, inputs, resize, resize)
        y = labels

        if cuda:
            x = x.cuda()
            y = y.cuda()

        # Forward pass
        outputs = model(x)
        loss = criterion(outputs, y)

        if is_training:
            optimiser.zero_grad()
            loss.backward()
            optimiser.step()

        _, predicted = outputs.max(1)
        accuracy = (predicted.data.cpu() == y.cpu()).float().mean()

        accuracies.append(accuracy)
        losses.append(loss.data.mean())

    diagnostics = {'loss': sum(losses) / len(losses),
                   'acc': sum(accuracies) / len(accuracies)}

    return diagnostics


for epoch in range(num_epochs):
    if is_training is True:
        diagnostics_train = run_epoch(loader_train)
        diagnostics_val = run_epoch(loader_val)
        diagnostics_train = dict({"type": "train", "epoch": epoch}, **diagnostics_train)
        diagnostics_val = dict({"type": "validation", "epoch": epoch}, **diagnostics_val)
        print(diagnostics_train)
        print(diagnostics_val)

        with open(logfile, 'a') as lf:
            lf.write(str(diagnostics_train))
            lf.write(str(diagnostics_val))
    else:
        diagnostics_val = run_epoch(loader_val)
        diagnostics_val = dict({"type": "validation", "epoch": epoch}, **diagnostics_val)
        print(diagnostics_val)

        with open(logfile, 'a') as lf:
            lf.write(str(diagnostics_val))

'''
SAVE PARAMETERS
'''
if is_training:
    weightsfile = os.path.join("weights_1.pkl")
    with open(weightsfile, "wb") as wf:
        pickle.dump(model.state_dict(), wf)

