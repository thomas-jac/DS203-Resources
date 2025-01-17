# -*- coding: utf-8 -*-
"""DS203-Assignment-9-Q1-XOR.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1cUAFoxISPpQMKG6DxyO7pQSTxe3AJxcg

# Defining Accelerator
"""

import torch

# Using the GPU if it's available for faster computation time
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

print(device)

"""# Importing Relevant Modules"""

import numpy as np
import matplotlib.pyplot as plt
 
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
 
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split

"""# Generating Random Data"""

np.random.seed(0)
data = 2*np.random.uniform(size = (10000, 2)) - 1
 
# Assigning labels
labels = np.zeros((10000, 1))
 
for i in range(10000):
 
    if (data[i][0] >= 0 and data[i][1] >= 0) or (data[i][0] <= 0 and data[i][1] <= 0):
        labels[i] = 0
 
    else:
        labels[i] = 1

# Sanity check on data
print("Data Point: ", data[100])
print("Label: ", labels[100])

# Splitting the data into the required fractions
X_train, X_test, Y_train, Y_test = train_test_split(data, labels, test_size = 0.3, shuffle = True)
X_val, X_test, Y_val, Y_test = train_test_split(X_test, Y_test, test_size = 0.5, shuffle = True)
 
# Sanity check on shapes
print(X_train.shape, Y_train.shape)
print(X_val.shape, Y_val.shape)
print(X_test.shape, Y_test.shape)

"""# Defining The Dataset Module"""

class XOR_Data(Dataset):
 
    def __init__(self, data, labels):
        self.data = data
        self.labels = labels
 
    def __len__(self):
        return len(self.data)
 
    def __getitem__(self, idx):
        
        # Converting to torch tensors
        point = torch.tensor(self.data[idx])
        label = torch.tensor(self.labels[idx])

        return point, label

# Creating instances of the dataset module
train_dataset = XOR_Data(X_train, Y_train)
val_dataset = XOR_Data(X_val, Y_val)
test_dataset = XOR_Data(X_test, Y_test)

# Creating DataLoader objects
train_loader = DataLoader(train_dataset, batch_size = 16, shuffle = True, drop_last = True)
val_loader = DataLoader(val_dataset, batch_size = 16, shuffle = True, drop_last = True)
test_loader = DataLoader(test_dataset, batch_size = 16, shuffle = True, drop_last = True)

"""# Defining The Model"""

class XOR_Model(nn.Module):
 
    def __init__(self, hidden_size):
 
        super().__init__()
 
        self.fc1 = nn.Linear(2, hidden_size)
        self.fc2 = nn.Linear(hidden_size, 1)
 
    def forward(self, x):
 
        x = F.relu(self.fc1(x))
        out = torch.sigmoid(self.fc2(x))
 
        return out

# Function to create instances of the model
def model_def(hidden_size=4, lr=0.003):
 
    model = XOR_Model(hidden_size)
    model = model.float()
    
    # Passing the model to the device
    model = model.to(device)    
 
    # Defining the loss function, optimizer and learning rate scheduler
    loss_func = nn.BCELoss()
    opt = optim.SGD(model.parameters(), lr)
    lr_scheduler = optim.lr_scheduler.ReduceLROnPlateau(opt, patience=5, verbose=True)
 
    return model, loss_func, opt, lr_scheduler

"""# Training Loop"""

def fit(model, loss_func, opt, lr_scheduler, train_loader, val_loader, n_epochs, print_info=True):
    
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
            loss = loss_func(out.float(), yb.float())
            
            # Classifying the output value points
            out_pred = torch.zeros((out.size()[0], 1))
            out_pred = out_pred.to(device)
 
            for i in range(len(out)):
                out_pred[i][0] = 1 if out[i][0] >= 0.5 else 0
 
            out_pred = out_pred.reshape(-1, 1)
            train_acc += (out_pred == yb).float().mean()
            train_loss += loss
 
            loss.backward()
            opt.step()
 
        train_loss /= len(train_loader)
        train_acc /= len(train_loader)
        train_losses.append(train_loss)
        train_accuracies.append(train_acc)

        lr_scheduler.step(train_loss)   #Setting up lr decay 
 
        # Setting the model to eval mode
        model.eval()
        with torch.no_grad():
 
            for xb, yb in val_loader:
 
                # Passing the data to the device
                xb = xb.to(device)
                yb = yb.to(device)
 
                # Computing the output from the model and loss
                out = model(xb.float())
                loss = loss_func(out.float(), yb.float())
            
                # Classifying the output value points
                out_pred = torch.zeros((out.size()[0], 1))
                out_pred = out_pred.to(device)
 
                for i in range(len(out)):
                    out_pred[i][0] = 1 if out[i][0] >= 0.5 else 0 
                
                out_pred = out_pred.reshape(-1, 1)
                val_acc += (out_pred == yb).float().mean()
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

model, loss_func, opt, lr_scheduler = model_def(4, 0.003)
 
train_losses, train_accuracies, val_losses, val_accuracies, best_val_loss = fit(model, loss_func, opt, lr_scheduler, train_loader, val_loader, 100)

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

"""# Tuning The Hidden Layer Hyperparameter"""

hidden_sizes = [2, 4, 6, 8, 10]
models = []

# Creating an array of models for different hidden layer sizes 
for hidden_size in hidden_sizes:
 
    models.append(model_def(hidden_size, 0.003))

# Keeping track of the best validation losses 
best_val_losses = []

# Training all models and computing the best validation losses 
for i in range(len(models)):
    
    print(f"\nTraining model with hidden layer size {hidden_sizes[i]} and optimizer with learning rate 0.003\n")
    train_losses, train_accuracies, val_losses, val_accuracies, best_val_loss = fit(models[i][0], models[i][1], models[i][2], models[i][3], train_loader, val_loader, 100, False)
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
 
    models.append(model_def(4, lr))
 
best_val_losses = []
 
# Training all models and computing the best validation losses 
for i in range(len(models)):
    
    print(f"\nTraining model with hidden layer size 4 and optimizer with learning rate {lr_choices[i]}\n")
    train_losses, train_accuracies, val_losses, val_accuracies, best_val_loss = fit(models[i][0], models[i][1], models[i][2], models[i][3], train_loader, val_loader, 20, False)
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

"""# Training The Best Validation Model

From the above two hyperparameter tunings on the validation set, we can observe that the best validation loss is obtained with a hidden layer size of 10 and a learning rate of 0.01
"""

model = model_def(10, 0.01)

train_losses, train_accuracies, val_losses, val_accuracies, best_val_loss = fit(model[0], model[1], model[2], model[3], train_loader, val_loader, 100)

"""# Predictions On The Test Set"""

# Setting the model to eval mode
model[0].eval()
with torch.no_grad():

    test_loss = 0
    test_acc = 0
    
    # To keep track of similarly labelled points by the model
    label_one = []
    label_zero = []
 
    for xb, yb in test_loader:
 
        # Passing the data to the device
        xb = xb.to(device)
        yb = yb.to(device)
 
        out = model[0](xb.float())
        loss = loss_func(out.float(), yb.float())
            
        # Computing the output from the model and assigning labels
        out_pred = torch.zeros((out.size()[0], 1))
        out_pred = out_pred.to(device)
 
        for i in range(len(out)):
        
            if out[i][0] >= 0.5:

                out_pred[i][0] = 1
                label_one.append(xb[i].cpu().numpy())

            else:

                out_pred[i][0] = 0
                label_zero.append(xb[i].cpu().numpy()) 

        out_pred = out_pred.reshape(-1, 1)
        test_acc += (out_pred == yb).float().mean()
        test_loss += loss

    test_loss /= len(test_loader)
    test_acc /= len(test_loader)

"""# Plotting The Predicted Data"""

label_one = np.array(label_one)
label_zero = np.array(label_zero)

print(f"Loss on the test set is {test_loss}")
print(f"Accuracy on the test set is {test_acc}")

plt.figure(figsize=(10,5))
plt.plot(label_one[:,0], label_one[:,1], marker='o', linestyle='', ms=12, label='Label 1')
plt.plot(label_zero[:,0], label_zero[:,1], marker='o', linestyle='', ms=12, label='Label 0')
plt.legend()
plt.show()