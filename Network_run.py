# Importing the libraries

import numpy as np
import random
import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torch.autograd as autograd
from torch.autograd import Variable


#Neural Network

class Network(nn.Module):
    
    def __init__(self, input_size, nb_action):
        super(Network, self).__init__()
        self.input_size = input_size
        self.nb_action = nb_action
        self.fc1 = nn.Linear(input_size, 30)
        self.fc2 = nn.Linear(30, nb_action)
    
    def forward(self, state):
        x = F.relu(self.fc1(state))
        q_values = self.fc2(x)
        return q_values

#Experience Replay

class ReplayMemory(object):
    
    def __init__(self, capacity):
        self.capacity = capacity
        self.memory = []
    
    def push(self, event):
        self.memory.append(event)
        if len(self.memory) > self.capacity:
            del self.memory[0]
    
    def sample(self, batch_size):
        samples = zip(*random.sample(self.memory, batch_size))
        return map(lambda x: Variable(torch.cat(x, 0)), samples)

# Main

class MainNetwork():
    
    def __init__(self, input_size, nb_action, gamma):
        self.gamma = gamma
        self.reward_window = []
        self.model = Network(input_size, nb_action)
        self.target_model = Network(input_size, nb_action)
        self.memory = ReplayMemory(100000)
        self.optimizer = optim.Adam(self.model.parameters(), lr = 0.01)
        self.last_state = torch.Tensor(input_size).unsqueeze(0)
        self.last_action = 0
        self.last_reward = 0
        self.target_cycle_count = 0
        self.tau = 0.9
        self.cycle_count = 25
        
    def select_action(self, state):
        probs = F.softmax(self.model(Variable(state, volatile = True))*100) # T=100
        action = probs.multinomial(num_samples=1)
        return action.data[0,0]
    
    def learn(self, batch_state, batch_next_state, batch_reward, batch_action):
        outputs = self.model(batch_state).gather(1, batch_action.unsqueeze(1)).squeeze(1)
        #next_outputs = self.model(batch_next_state).detach().max(1)[0]
        #target = self.gamma*next_outputs + batch_reward
        
        target_outputs = self.target_model(batch_state).gather(1, batch_action.unsqueeze(1)).squeeze(1)
        target_next_outputs = self.target_model(batch_next_state).detach().max(1)[0]
        target_target = self.gamma*target_next_outputs + batch_reward
        
        #td_loss = F.smooth_l1_loss(outputs, target)
        td_loss = F.smooth_l1_loss(outputs, target_target)
        self.optimizer.zero_grad()
        #td_loss.backward(retain_variables = True)
        td_loss.backward()
        self.optimizer.step()
        
        if self.target_cycle_count > self.cycle_count :
            #self.target_model = copy.deepcopy(self.model)
            self.cycle_count = 1000
            for target_param, param in zip(self.target_model.parameters(), self.model.parameters()):
                target_param.data.copy_(self.tau * param + (1 - self.tau) * target_param)
            self.target_cycle_count = 0
            print("target reloaded")
            
        self.target_cycle_count += 1
        #print(self.target_cycle_count)
    
    def update(self, reward, new_signal):
        new_state = torch.Tensor(new_signal).float().unsqueeze(0)
        self.memory.push((self.last_state, new_state, torch.LongTensor([int(self.last_action)]), torch.Tensor([self.last_reward])))
        action = self.select_action(new_state)
        if len(self.memory.memory) > 100:
            batch_state, batch_next_state, batch_action, batch_reward = self.memory.sample(100)
            self.learn(batch_state, batch_next_state, batch_reward, batch_action)
        self.last_action = action
        self.last_state = new_state
        self.last_reward = reward
        self.reward_window.append(reward)
        if len(self.reward_window) > 1000:
            del self.reward_window[0]
        return action
    
    def score(self):
        return sum(self.reward_window)/(len(self.reward_window)+1.)
    
    def save(self, scores, file_name):
        torch.save({'state_dict': self.model.state_dict(),
                    'optimizer' : self.optimizer.state_dict(),
                   }, 'last_brain.pth')
        torch.save({'state_dict': self.model.state_dict(),
                    'optimizer' : self.optimizer.state_dict(),
                    'scores': scores,
                   }, file_name + '.pth')
        torch.save({'state_dict': self.target_model.state_dict(),
#                    'optimizer' : self.optimizer.state_dict(),
                   }, 'last_target_brain.pth')
        torch.save({'state_dict': self.target_model.state_dict(),
#                    'optimizer' : self.optimizer.state_dict(),
                    'scores': scores,
                   }, file_name + 'target.pth')
    
    def load(self):
           
        if os.path.isfile('last_brain.pth'):
            print("=> loading checkpoint... ")
            checkpoint = torch.load('last_brain.pth')
            self.model.load_state_dict(checkpoint['state_dict'])
            self.optimizer.load_state_dict(checkpoint['optimizer'])
            print("last_brain load done !")
        else:
            print("no checkpoint found for last_brain...")
            
    
    def target_load(self):
        
        if os.path.isfile('last_target_brain.pth'):
            print("=> loading checkpoint... ")
            checkpoint = torch.load('last_target_brain.pth')
            self.target_model.load_state_dict(checkpoint['state_dict'])
#            self.optimizer.load_state_dict(checkpoint['optimizer'])
            print("last_target_brain load done !")
        else:
            print("no checkpoint found for last_target_brain...")
            
            
            