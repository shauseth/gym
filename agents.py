import numpy as np

class TDZeroAgent:
    """Tabular TD(0) for estimating v_pi"""
    def __init__(self, n_states):
        self.alpha = None
        self.gamma = None
        self.values = np.zeros(n_states)
        self.last_state = None

    def start(self, state):
        self.last_state = state

    def step(self, state, reward):
        delta = reward + self.gamma * self.values[state] - self.values[self.last_state]
        self.values[self.last_state] += self.alpha * delta
        self.last_state = state

    def end(self, reward):
        delta = reward - self.values[self.last_state]
        self.values[self.last_state] += self.alpha * delta

class SarsaLambdaAgent:
    """Sarsa(λ) with binary features and linear function approximation for estimating q_pi"""
    def __init__(self, num_actions, tilecoder):
        self.num_actions = num_actions
        self.tilecoder = tilecoder
        self.iht_size = tilecoder.iht.size
        self.epsilon = None
        self.gamma = None
        self.alpha = None
        self.lambd = None
        self.w = np.zeros([self.num_actions, self.iht_size])
        self.z = np.zeros([self.num_actions, self.iht_size])
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