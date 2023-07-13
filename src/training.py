import gym as GYM  
import itertools as IT  
import matplotlib as MPLOT  
import matplotlib.style as MPLOTS  
import numpy as nmp  
import pandas as pnd  
import sys  
from collections import defaultdict as DD 

env = gym.make("FrozenLake-v1")  
n_observations1 = env.observation_space.n  
n_actions1 = env.action_space.n  

def createEpsilonGreedyPolicy1(Q1, epsilon1, num_actions1):  
    def policyFunction1(state):  
  
        Action_probabilities = nmp.ones(num_actions1,  
                dtype = float) * epsilon1 / num_actions1  
                  
        best_action = nmp.argmax(Q1[state])  
        Action_probabilities[best_action] += (1.0 - epsilon1)  
        return Action_probabilities  
  
    return policyFunction1

def qLearning1(env, num_episodes1, discount_factor = 1.0,  
                            alpha = 0.6, epsilon1 = 0.1):    
    Q1 = DD(lambda: nmp.zeros(env.action_space.n))  
  
    stats = MPLOT.EpisodeStats(  
        episode_lengths = nmp.zeros(num_episodes1),  
        episode_rewards = nmp.zeros(num_episodes1))   
      
    policy = createEpsilonGreedyPolicy1(Q1, epsilon1, env.action_space.n)  
      
    for Kth_episode in range(num_episodes1):  
        state = env.reset()  
          
        for J in itertools.count():  
            action_probabilities1 = policy(state)  
            action = nmp.random.choice(nmp.arange(  
                    len(action_probabilities1)),  
                    p = action_probabilities1)   
            next_state, reward, done, _ = env.step(action)  
            stats.episode_rewards[Kth_episode] += reward  
            stats.episode_lengths[Kth_episode] = J                
            best_next_action = nmp.argmax(Q1[next_state])     
            td_target = reward + discount_factor * Q1[next_state][best_next_action]  
            td_delta = td_target - Q1[state][action]  
            Q1[state][action] += alpha * td_delta  
            if done:  
                break  
                  
            state = next_state  
      
    return Q1, stats  