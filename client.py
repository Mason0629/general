# -*- coding: utf-8 -*-
# @Time    : 2020-02-01 20:40
# @Author  : Enjoy Zhao

import tensorflow as tf
import general as gr
import os
import configparser
if not os.path.exists("model_dir"):
      os.makedirs("model_dir")

class client(object):

    def __init__(self,dense_num=None,cell_num=None,activation=None,action_space=0,train_steps=3000,run_steps=1000,dummy_env=None,model_name=None,algorithm_type=None):

        self.dense_num=dense_num
        self.cell_num=cell_num
        self.activation=activation
        self.train_steps=train_steps
        self.run_steps=run_steps
        self.dummy_env=dummy_env
        self.model_name=model_name
        self.file_path="model_dir/"+model_name
        self.config_path="model_dir/"+model_name+".cfg"
        self.algorithm_type=algorithm_type
        self.run_steps=run_steps
        self.action_space=action_space
        self.ep_reward=0
        self.ep_step=0
        self.done=False


    def create_model(self):
        model = tf.keras.Sequential()
        model.add(tf.keras.layers.Dense(16, activation='relu', input_shape=self.dummy_env.observation_space.shape))
        for i in range(self.dense_num):
            model.add(tf.keras.layers.Dense(self.cell_num,activation=self.activation ))
        return model


    def plot_rewards(self,episode_rewards, episode_steps, done=False):

        self.ep_reward=episode_rewards[0][-1]

        self.ep_step=episode_steps[0][-1]
        self.done=done

    def create_agent(self):
        model = self.create_model()
        if self.action_space ==0:
            self.action_space=self.dummy_env.action_space.n
        if self.algorithm_type=='dqn':
            agent = gr.DQN(model, actions=self.action_space, nsteps=2)
        elif self.algorithm_type=='ddpg':
            agent = gr.DDPG(model, actions=self.action_space, nsteps=2)

        elif self.algorithm_type=='ppo':
            agent = gr.PPO(model, actions=self.action_space, nsteps=2)

        return agent


    def train(self):

        # 将定义好的网络作为参数传入框架的API中，构成一个完成智能体，用于接下来的强化学习训练。
        agent =self.create_agent()
        cpkt = tf.io.gfile.listdir("model_dir")
        if cpkt==self.file_path:
            agent.model.load_weights(self.file_path)


        # 使用general框架的trainer来创建一个训练模拟器，在模拟器中进行训练。
        sim = gr.Trainer(self.dummy_env, agent)
        sim.train(max_steps=self.train_steps, visualize=True, plot=self.plot_rewards)
        agent.save(filename=self.file_path,overwrite=True,save_format='h5')
        cf = configparser.ConfigParser(allow_no_value=True)
        cf.add_section('ints')
        cf.add_section('strings')
        cf.set('ints', 'dense_num', "%s"%self.dense_num)
        cf.set('ints', 'cell_num', "%s"%self.cell_num)
        cf.set('ints', 'action_space', "%s" % self.action_space)
        cf.set('strings', 'activation',"%s"%self.activation)
        cf.set('strings', 'algorithm_type', "%s"%self.algorithm_type)
        with open(self.config_path, 'w') as f:
            cf.write(f)

    def run_model(self):
        agent = self.create_agent()
        agent.model.load_weights(filepath=self.file_path)
        sim = gr.Trainer(self.dummy_env, agent)
        sim.test(max_steps=self.run_steps,plot=self.plot_rewards)



