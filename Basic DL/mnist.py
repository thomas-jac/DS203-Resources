# -*- coding: utf-8 -*-
"""DS203-Assignment-9-Q2-MNIST.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/11PplmyRAYEsSzR_ADM6RV_FDlYGuyuHC

# Defining The Accelerator
"""

import torch

# Using the GPU if it's available for faster computation time
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

print(device)

"""# Importing Relevant Modules"""

import numpy as np
import matplotlib.pyplot as plt

import torchvision 
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchvision.transforms as transforms
import torchvision.transforms.functional as TF
 
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split

"""# Loading The Data"""

BATCH_SIZE = 16

# torchvision.datasets.MNIST outputs a set of PIL images
# We transform them to tensors
transform = transforms.ToTensor()

# Load and transform data
trainset = torchvision.datasets.MNIST('/tmp', train=True, download=True, transform=transform)
train_loader = torch.utils.data.DataLoader(trainset, batch_size=BATCH_SIZE, shuffle=True, num_workers=2)

valset = torchvision.datasets.MNIST('/tmp', train=False, download=True, transform=transform)
val_loader = torch.utils.data.DataLoader(valset, batch_size=BATCH_SIZE, shuffle=False, num_workers=2)

# Sanity check of the data
for image, label in train_loader:

    img = np.array(TF.to_pil_image(image[0]))
    print("Label: ", label[0])
    plt.imshow(img, cmap='gray')
    plt.show()
    break

print("Total training images: ", len(trainset))
print("Total validation/test images: ", len(valset))

"""# Defining The Basic Model"""

class MNIST_Linear(nn.Module):
 
    def __init__(self, hidden_size):
 
        super().__init__()
 
        self.fc1 = nn.Linear(784, hidden_size)
        self.fc2 = nn.Linear(hidden_size, 10)
 
    def forward(self, x):
        
        x = torch.flatten(x, start_dim=1)
        x = F.relu(self.fc1(x))
        out = self.fc2(x)
 
        return out

# Function to create instances of the model
def model_linear_def(hidden_size=128, lr=0.003):
 
    model = MNIST_Linear(hidden_size)
    model = model.float()
    
    # Passing the model to the device
    model = model.to(device)    
 
    # Defining the loss function, optimizer and learning rate scheduler
    loss_func = nn.CrossEntropyLoss()
    opt = optim.SGD(model.parameters(), lr)
 
    return model, loss_func, opt

"""# Basic Training Loop"""

def fit(model, loss_func, opt, train_loader, val_loader, n_epochs, print_info=True):
    
    # Defining arrays to track the loss and accuracy values
    train_losses = []
    train_accuracies = []
    val_losses = []
    val_accuracies = []
    
    # Defining an initial best validation loss
    best_val_loss = 1000
 
    for epoch in range(n_epochs):
 
        # Setting the model to training mode
        model.train()
        
        train_loss = 0
        train_acc = 0
        val_loss = 0
        val_acc = 0
 
        for xb, yb in train_loader:
 
            opt.zero_grad()

            # Passing the data to the device
            xb = xb.to(device)
            yb = yb.to(device)
 
            # Computing the output from the model and loss
            out = model(xb.float())
            loss = loss_func(out, yb.squeeze())

            # Carrying out output predictions and calculating accuracy
            train_pred = torch.argmax(out, dim = 1)
            train_pred = train_pred.reshape(train_pred.size()[0], 1)
            yb = yb.reshape(yb.size()[0], 1)
            train_acc += (train_pred == yb).float().mean()
            train_loss += loss
 
            loss.backward()
            opt.step()
 
        train_loss /= len(train_loader)
        train_acc /= len(train_loader)
        train_losses.append(train_loss)
        train_accuracies.append(train_acc)
 
        # Setting the model to eval mode
        model.eval()
        with torch.no_grad():
 
            for xb, yb in val_loader:
 
                # Passing the data to the device
                xb = xb.to(device)
                yb = yb.to(device)
 
                # Computing the output from the model and loss
                out = model(xb.float())
                loss = loss_func(out, yb.squeeze())

                # Carrying out output predictions and calculating accuracy
                val_pred = torch.argmax(out, dim = 1)
                val_pred = val_pred.reshape(val_pred.size()[0], 1)
                yb = yb.reshape(yb.size()[0], 1)
                val_acc += (val_pred == yb).float().mean()
                val_loss += loss
 
            val_loss /= len(val_loader)
            val_acc /= len(val_loader)
            val_losses.append(val_loss)
            val_accuracies.append(val_acc)
 
            if best_val_loss > val_loss:
                best_val_loss = val_loss
 
        if print_info:
            print("Epoch ", epoch+1, " Training Loss: ", train_loss, "CV Loss: ", val_loss)
            print("Training Acc: ", train_acc, "CV Acc: ", val_acc)
 
    return train_losses, train_accuracies, val_losses, val_accuracies, best_val_loss

model, loss_func, opt = model_linear_def()
 
train_losses, train_accuracies, val_losses, val_accuracies, best_val_loss = fit(model, loss_func, opt, train_loader, val_loader, 100)

epoch_array = [i for i in range(1, 101)]

# Plotting the training and validation data and setting axis parameters 
plt.figure(figsize = (15, 5))
plt.plot(epoch_array, train_losses, 'r', label='Training Loss')
plt.plot(epoch_array, val_losses, 'b', label='Validation Loss')
plt.tick_params(axis='x', which='major', labelsize=12)
plt.xlabel("Epoch", fontsize = 14)
plt.tick_params(axis='y', which='major', labelsize=12)
plt.ylabel("Loss", fontsize = 14)
plt.legend()
plt.show()
 
plt.figure(figsize = (15, 5))
plt.plot(epoch_array, train_accuracies, 'r', label='Training Accuracy')
plt.plot(epoch_array, val_accuracies, 'b', label='Validation Accuracy')
plt.tick_params(axis='x', which='major', labelsize=12)
plt.xlabel("Epoch", fontsize = 14)
plt.tick_params(axis='y', which='major', labelsize=12)
plt.ylabel("Accuracy", fontsize = 14)
plt.legend()
plt.show()

"""# Tuning The Hidden Layer Size Hyperparameter"""

hidden_sizes = [32, 64, 128, 256, 512]
models = []

# Creating an array of models for different hidden layer sizes 
for hidden_size in hidden_sizes:
 
    models.append(model_linear_def(hidden_size, 0.003))

# Keeping track of the best validation losses 
best_val_losses = []

# Training all models and computing the best validation losses 
for i in range(len(models)):
    
    print(f"\nTraining model with hidden layer size {hidden_sizes[i]} and optimizer with learning rate 0.003\n")
    train_losses, train_accuracies, val_losses, val_accuracies, best_val_loss = fit(models[i][0], models[i][1], models[i][2], train_loader, val_loader, 20, False)
    best_val_losses.append(best_val_loss)

# Plotting the data and setting various axis parameters 
plt.figure(figsize = (15, 5))
plt.plot(hidden_sizes, best_val_losses, label='Best Validation Loss')
plt.tick_params(axis='x', which='major', labelsize=12)
plt.xlabel("Hidden Layer Size", fontsize = 14)
plt.tick_params(axis='y', which='major', labelsize=12)
plt.ylabel("Best Validation Loss", fontsize = 14)
plt.show()

"""# Tuning The Learning Rate Hyperparameter"""

lr_choices = [0.00001, 0.0001, 0.001, 0.01, 0.1]
models = []
 
# Creating an array of models for different learning rates
for lr in lr_choices:
 
    models.append(model_linear_def(128, lr))
 
best_val_losses = []
 
# Training all models and computing the best validation losses 
for i in range(len(models)):
    
    print(f"\nTraining model with hidden layer size 128 and optimizer with learning rate {lr_choices[i]}\n")
    train_losses, train_accuracies, val_losses, val_accuracies, best_val_loss = fit(models[i][0], models[i][1], models[i][2], train_loader, val_loader, 20, False)
    best_val_losses.append(best_val_loss)

# Plotting the data and setting various axis parameters 
plt.figure(figsize = (15, 5))
plt.plot(lr_choices, best_val_losses, label='Best Validation Loss')
plt.tick_params(axis='x', which='major', labelsize=12)
plt.xscale('log')
plt.xlabel("Learning Rate", fontsize = 14)
plt.tick_params(axis='y', which='major', labelsize=12)
plt.ylabel("Best Validation Loss", fontsize = 14)
plt.show()

"""The training accuracy here has reached 1 while the CV accuracy is still less for a learning rate of 0.1 after training for 20 epochs, which clearly demonstrates that the model has overfit. In the next section, I will define a new model utilising CNN's and dropout layers to overcome the problem of overfitting

# Extra Credit Parts - CNN Model
"""

class Mnist_CNN(nn.Module):
    
    def __init__(self):
        
        super().__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size = 5, stride = 1, padding = 2)
        self.conv1_bn = nn.BatchNorm2d(32)
        self.conv2 = nn.Conv2d(32, 32, kernel_size = 5, stride = 1, padding = 2)
        self.conv2_bn = nn.BatchNorm2d(32)
        self.conv2_drop = nn.Dropout2d(0.25)
        self.conv3 = nn.Conv2d(32, 64, kernel_size = 3, stride = 1, padding = 1)
        self.conv3_bn = nn.BatchNorm2d(64)
        self.conv4 = nn.Conv2d(64, 64, kernel_size = 3, stride = 1, padding = 1)
        self.conv4_bn = nn.BatchNorm2d(64)
        self.conv4_drop = nn.Dropout2d(0.25)
        self.fc1 = nn.Linear(3136, 256)
        self.fc1_bn = nn.BatchNorm1d(256)
        self.fc1_drop = nn.Dropout(0.5)
        self.fc2 = nn.Linear(256, 10)
    
    def forward(self, xb):
        
        xb = xb.view(-1, 1, 28, 28)
        xb = F.relu(self.conv1(xb))
        xb = self.conv1_bn(xb)
        xb = F.relu(self.conv2(xb))
        xb = self.conv2_bn(xb)
        xb = F.max_pool2d(xb, (2, 2))
        xb = self.conv2_drop(xb)
        xb = F.relu(self.conv3(xb))
        xb = self.conv3_bn(xb)
        xb = F.relu(self.conv4(xb))
        xb = self.conv4_bn(xb)
        xb = F.max_pool2d(xb, (2, 2), stride = 2)
        xb = self.conv4_drop(xb)
        xb = xb.view(-1, self.num_flat_features(xb))
        xb = F.relu(self.fc1(xb))
        xb = self.fc1_bn(xb)
        xb = self.fc1_drop(xb)
        xb = self.fc2(xb)
        
        return xb
  
    def num_flat_features(self, xb):
        
        size = xb.size()[1:]
        num_features = 1
        for s in size:
            num_features *= s
        return num_features

model = Mnist_CNN()
model = model.float()
model = model.to(device)

from torch.utils.tensorboard import SummaryWriter

writer = SummaryWriter('runs/mnist_cnn_1')

# get some random training images
dataiter = iter(train_loader)
images, labels = dataiter.next()

# create grid of images
img_grid = torchvision.utils.make_grid(images)

# write to tensorboard
writer.add_image('four_fashion_mnist_images', img_grid)

!tensorboard --logdir=runs

loss_func = nn.CrossEntropyLoss()
opt = optim.Adam(model.parameters(), lr=0.001)
lr_scheduler = optim.lr_scheduler.ReduceLROnPlateau(opt, patience=2, verbose=True)

def fit(model, loss_func, opt, train_loader, val_loader, n_epochs):

    for epoch in range(n_epochs):
 
        # Setting the model to training mode
        model.train()
        
        train_loss = 0
        train_acc = 0
        val_loss = 0
        val_acc = 0
 
        for xb, yb in train_loader:
 
            opt.zero_grad()

            # Passing the data to the device
            xb = xb.to(device)
            yb = yb.to(device)
 
            # Computing the output from the model and loss
            out = model(xb.float())
            loss = loss_func(out, yb.squeeze())

            # Carrying out output predictions and calculating accuracy
            train_pred = torch.argmax(out, dim = 1)
            train_pred = train_pred.reshape(train_pred.size()[0], 1)
            yb = yb.reshape(yb.size()[0], 1)
            train_acc += (train_pred == yb).float().mean()
            train_loss += loss
 
            loss.backward()
            opt.step()
 
        train_loss /= len(train_loader)
        train_acc /= len(train_loader)

        lr_scheduler.step(train_loss)
 
        # Setting the model to eval mode
        model.eval()
        with torch.no_grad():
 
            for xb, yb in val_loader:
 
                # Passing the data to the device
                xb = xb.to(device)
                yb = yb.to(device)
 
                # Computing the output from the model and loss
                out = model(xb.float())
                loss = loss_func(out, yb.squeeze())

                # Carrying out output predictions and calculating accuracy
                val_pred = torch.argmax(out, dim = 1)
                val_pred = val_pred.reshape(val_pred.size()[0], 1)
                yb = yb.reshape(yb.size()[0], 1)
                val_acc += (val_pred == yb).float().mean()
                val_loss += loss
 
            val_loss /= len(val_loader)
            val_acc /= len(val_loader)
            
        '''
        writer.add_scalar('Training Loss', train_loss, epoch)
        writer.add_scalar('Validation Loss', val_loss, epoch)
        '''

        print("Epoch ", epoch+1, " Training Loss: ", train_loss, "CV Loss: ", val_loss)
        print("Training Acc: ", train_acc, "CV Acc: ", val_acc)

fit(model, loss_func, opt, train_loader, val_loader, 20)