import gym
import numpy as np
env = gym.make('CartPole-v0')
a = env.action_space
o = env.observation_space






nn.init()

print(nn.calculate(np.array([0.5,0.5,0.5,0.5])))
exit()
for i_episode in range(20):
    observation = env.reset()
    points = 0
    for t in range(100):
        env.render()
        action = env.action_space.sample()
        observation, reward, done, info = env.step(1)
        points += reward

        if done:
            print(f"Points: {points}")
            break
env.close()