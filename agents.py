import numpy as np
import tiles3 as tc

class TileCoder:

    def __init__(self, iht_size):
        self.iht = tc.IHT(iht_size)

    def get_tiles(self, state):
        pass

class SarsaLambdaAgent:

    def __init__(self):
        self.num_actions = 3
        self.iht_size = 16384
        self.epsilon = 0.0
        self.gamma = 1.0
        self.alpha = 0.2 / 48
        self.lambd = 0.9
        self.w = np.zeros([self.num_actions, self.iht_size])
        self.z = np.zeros([self.num_actions, self.iht_size])
        self.tilecoder = TileCoder(self.iht_size)
        self.last_action = None
        self.last_tiles = None

    def select_action(self):
        pass

    def start(self, state):
        pass

    def step(self, state, reward):
        pass

    def end(self, reward):
        pass