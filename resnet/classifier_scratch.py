"""This file is used to train the ResNet50 from scratch. Initally the model is 
initialized with random weights, instead of pretrained."""

import numpy as np, argparse, json

import matplotlib.pyplot as plt
from PIL import Image

import torch
import torchvision
from torchvision import datasets, models, transforms
import torch.nn as nn
import torch.backends.cudnn as cudnn
from torch.nn import functional as F
import torch.optim as optim

# Check for GPU availibility
device = 'cuda' if torch.cuda.is_available() else 'cpu'
# Flag to decide if to use mixed precision loss or not
amp = True  # mixed precision

'''
Load the hyperparamter config, either
config_scratch_big.json : with batch size 64 (can be done with multiple GPUs only)
config_scratch.json : with batch size 16 (if only single GPU)
'''
with open('configs/config_scratch_big.json', 'r') as f:
    config = json.load(f)

### Hyperparamters
learning_rate = config['learning_rate']
epochs = config['num_epochs']
batch_size = config['batch_size']
weight_decay = config['weight_decay']
momentum = config['momentum']
adaptivity = config['adaptivity']
max_lr = config['max_lr']

## Transform function
normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])

## Using auto augment for CIFAR-10                                 
transforms = {
    'train':
    transforms.Compose([
        transforms.Resize((224,224)),
        transforms.AutoAugment(transforms.AutoAugmentPolicy.CIFAR10),
        transforms.ToTensor(),
        normalize
    ]),
    'validation':
    transforms.Compose([
        transforms.Resize((224,224)),
        transforms.ToTensor(),
        normalize
    ]),
}

# Load the dataset
image_datasets = {
    'train': 
    torchvision.datasets.CIFAR10(
    root='dataset/cifar-10-batches-py', train=True, download=True, transform = transforms['train']),
    'validation': 
    torchvision.datasets.CIFAR10(
    root='dataset/cifar-10-batches-py', train=False, download=True, transform=transforms['validation'])
}

dataloaders = {
    'train':
    torch.utils.data.DataLoader(image_datasets['train'],
                                batch_size=batch_size,
                                shuffle=True,
                                num_workers=0),  
    'validation':
    torch.utils.data.DataLoader(image_datasets['validation'],
                                batch_size=batch_size,
                                shuffle=False,
                                num_workers=0)  
}

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(device)

# Use autocast decorator in the forward method for mixed precision loss
class ResNet(nn.Module):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.model = models.resnet50(*args, **kwargs)

    def forward(self, *args, **kwargs):
        with torch.cuda.amp.autocast(enabled=amp):
            return self.model(*args, **kwargs)

# FC layer is only with 10 hidden units
model = ResNet(pretrained=False, num_classes=10).to(device)
if device == 'cuda':
    model = torch.nn.DataParallel(model)
    cudnn.benchmark = True

# Not needed, as we want to update the gradients    
'''for param in model.parameters():
    param.requires_grad = False'''   

## Model specifiers
optimizer = optim.Adam(model.parameters(), lr=learning_rate, weight_decay = weight_decay)
scheduler = torch.optim.lr_scheduler.OneCycleLR(optimizer, max_lr=max_lr, steps_per_epoch=len(dataloaders['train']), epochs=epochs)
criterion = nn.CrossEntropyLoss()

def run_model(model, criterion, optimizer, num_epochs=epochs):
    scaler = torch.cuda.amp.GradScaler(enabled=amp)
    
    for epoch in range(num_epochs):
        print('Epoch {}/{}'.format(epoch+1, num_epochs))
        print('-' * 10)

        for phase in ['train', 'validation']:
            print(phase)
            if phase == 'train':
                model.train()
            else:
                model.eval()

            running_loss = 0.0
            running_corrects = 0
            total_accuracy = 0 

            for inputs, labels in dataloaders[phase]:
                inputs = inputs.to(device)
                labels = labels.to(device)

                with torch.cuda.amp.autocast(enabled=amp):
                    outputs = model(inputs)
                    loss = criterion(outputs, labels)

                # Added mixed precision support and one cycle LR scheduler
                if phase == 'train':
                    optimizer.zero_grad()
                    scaler.scale(loss).backward()
                    scaler.step(optimizer)
                    scaler.update()
                    scheduler.step()

                _, preds = torch.max(outputs, 1)
                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == labels.data)

                accuracy = (outputs.argmax(-1) == labels).float().mean()
                total_accuracy += accuracy

            epoch_loss = running_loss / len(image_datasets[phase])
            epoch_acc = total_accuracy / len(dataloaders[phase])

            print('{} loss: {:.4f}, acc: {:.4f}'.format(phase,
                                                        epoch_loss,
                                                        epoch_acc))          
    return model

model_trained = run_model(model, criterion, optimizer, num_epochs=epochs)
print("======> This is the classifier with non pretrained weights")

print("======> This is the model")
print(model)

print("Parameters used for this model")
for key, value in config.items():  
    print(key, value)

# Save the wights of the trained model
torch.save(model_trained.state_dict(), 'saved_model/pytorch/weights_scratch.h5')








