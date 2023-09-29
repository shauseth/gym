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

    def select_action(self, tiles):
        choice = 'greedy' if np.random.random() > self.epsilon else 'epsilon'
        action_values = self.w[:, tiles].sum(axis=1)
        action = action_values.argmax() if choice == 'greedy' else np.random.choice(self.num_actions)
        return action

    def start(self, state):
        tiles = self.tilecoder.get_tiles(state)
        action = self.select_action(tiles)
        self.z *= 0.0
        self.last_action = action
        self.last_tiles = tiles.copy()
        return self.last_action

    def step(self, state, reward):
        tiles = self.tilecoder.get_tiles(state)
        action = self.select_action(tiles)
        delta = reward
        for i in self.last_tiles:
            delta -= self.w[self.last_action][i]
            self.z[self.last_action][i] = 1
        for i in tiles:
            delta += self.gamma * self.w[action][i]
        self.w += self.alpha * delta * self.z
        self.z *= self.gamma * self.lambd
        self.last_action = action
        self.last_tiles = tiles.copy()
        return self.last_action

    def end(self, reward):
        delta = reward
        for i in self.last_tiles:
            delta -= self.w[self.last_action][i]
            self.z[self.last_action][i] = 1
        self.w += self.alpha * delta * self.z