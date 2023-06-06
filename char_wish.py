# Notebook: https://deepnote.com/workspace/omicron-9d7e-2559ece8-2934-4573-8527-29118c415320/project/Random-Ideas-01836615-5a67-4ae6-9e35-438591328c47/notebook/Genshin%20Impact-f8f3f7cd897c4bb6b839646365447f11

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import math
import random

FIVE_STAR_PROB = 0.006
FIVE_STAR_UP = 0.5
MAX_NO_FIVE_STAR_STREAK = 89
FIVE_STAR_BOOST_AT = 72
FOUR_STAR_PROB = 0.051
MAX_NO_FOUR_STAR_STREAK = 9
HIT_FIVE_STAR_IN_FOUR_STAR_GUARANTEE = 0.006
FOUR_STAR_UP = 0.5
NUM_FOUR_STAR_UP = 3

class Lottory:
    def __init__(self,
                 no_four_star_streak = 0,
                 no_five_star_streak = 0,
                 last_five_star_no_up = False,
                 last_four_star_no_up = False,
                 ):
        self.input_no_five_star_streak = no_five_star_streak
        self.input_no_four_star_streak = no_four_star_streak
        self.input_last_five_star_no_up = last_five_star_no_up
        self.input_last_four_star_no_up = last_four_star_no_up        
        self.reset()        

    def reset(self):
        self.five_star_random_char_hit = 0
        self.five_star_up_char_hit = 0
        self.four_star_random_hit = 0
        self.four_star_up_char_hit = {0: 0, 1:0, 2: 0}
        self.no_four_star_streak = self.input_no_four_star_streak
        self.no_five_star_streak = self.input_no_five_star_streak
        self.last_five_star_no_up = self.input_last_five_star_no_up
        self.last_four_star_no_up = self.input_last_four_star_no_up
        self.num_four_star_guarantee = 0
        self.num_five_star_guarantee = 0
        self.five_star_up_dist = []
        self.four_star_up_target_dist = []         

    def hit_five_star(self):
        self.no_five_star_streak = 0
        if self.last_five_star_no_up or random.random() < FIVE_STAR_UP:
            # Hit UP
            self.last_five_star_no_up = False
            self.five_star_up_char_hit += 1
        else:
            # Hit other 5 star
            self.last_five_star_no_up = True
            self.five_star_random_char_hit += 1        

    def hit_four_star(self):
        self.no_four_star_streak = 0
        if self.last_four_star_no_up or random.random() < FOUR_STAR_UP:
            # Hit four star char up
            self.last_four_star_no_up = False
            who = random.randint(0, NUM_FOUR_STAR_UP-1)
            self.four_star_up_char_hit[who] += 1
        else:
            # Hit other four star
            self.last_four_star_no_up = True
            self.four_star_random_hit += 1     

    def cur_five_star_prob(self):
        wish_id = 1 + self.no_five_star_streak
        if wish_id <= 73:
            return FIVE_STAR_PROB
        else:
            return FIVE_STAR_PROB + (wish_id - 73) * FIVE_STAR_PROB * 10

    def cur_four_star_prob(self):
        wish_id = 1 + self.no_four_star_streak
        if wish_id <= 8:
            return FOUR_STAR_PROB
        else:
            return FOUR_STAR_PROB + (wish_id - 8) * FOUR_STAR_PROB * 10        

    def is_five_star_hit(self, roll):
        wish_id = 1 + self.no_five_star_streak
        if wish_id == MAX_NO_FIVE_STAR_STREAK + 1:
            self.num_five_star_guarantee += 1
        return 0 <= roll < self.cur_five_star_prob()

    def is_four_star_hit(self, roll):
        wish_id = 1 + self.no_four_star_streak
        if wish_id == MAX_NO_FOUR_STAR_STREAK + 1:
            self.num_four_star_guarantee += 1

        base = self.cur_five_star_prob()
        return base <= roll < base + self.cur_four_star_prob()


    def wish_once(self):
        roll = random.random() # A float number in [0, 1)       
        if self.is_five_star_hit(roll):
            # Hit five star
            self.hit_five_star()
            self.no_four_star_streak += 1
            return
        else:
            self.no_five_star_streak += 1                      

        if self.is_four_star_hit(roll):
            # Hit four star
            self.hit_four_star()
            return

        self.no_four_star_streak += 1

    def simulate_once(self, num_wishes, verbose = False):
        self.reset()
        num = num_wishes

        for i in range(num):
            self.wish_once()

        self.total_four_star_hit = self.four_star_random_hit + sum(self.four_star_up_char_hit.values())
        self.total_five_star_hit = self.five_star_random_char_hit + self.five_star_up_char_hit

        if verbose:
            print("After %d simulation" % num)
            print("5 Star up hit: %d (%.2f%%)" % 
                (self.five_star_up_char_hit,
                self.five_star_up_char_hit / num * 100))
            print("5 Star random hit: %d (%.2f%%)" % 
                (self.five_star_random_char_hit, self.five_star_random_char_hit / num * 100))
            print("5 Star total hit: %d (%.2f%%), 5 star guarantee: %d" % 
                (self.total_five_star_hit, self.total_five_star_hit / num * 100,
                self.num_five_star_guarantee))
            print('=' * 30)
            print("4 Star total hit: %d (%.2f%%)\nup hit: %s (%.2f%%)\n4 star guarantee: %d" % 
                (self.total_four_star_hit, self.total_four_star_hit / num * 100,
                self.four_star_up_char_hit.items(),
                sum(self.four_star_up_char_hit.values()) / num * 100, self.num_four_star_guarantee))

    def monte_carlo(self, num_sim, num_wishes):
        five_star_up_dist = []
        four_star_up_target_dist = [] 
        for i in range(num_sim):
            self.simulate_once(num_wishes)
            five_star_up_dist.append(self.five_star_up_char_hit)
            four_star_up_target_dist.append(self.four_star_up_char_hit[0])

        self.five_star_up_dist = pd.Series(five_star_up_dist)
        self.four_star_up_target_dist = pd.Series(four_star_up_target_dist)
        return self.five_star_up_dist, self.four_star_up_target_dist

    def display(self):
        plt.figure(figsize=(16, 16))

        dist = self.five_star_up_dist
   
        mean = dist.mean()
        data = dist.value_counts().sort_index(ascending=False)
        total = data.sum()
        data = pd.DataFrame({'count': data.index, 'prob': data / total, 'cum_prob': (data / total).cumsum()})
        data.reset_index(inplace=True, drop=True)

        plt.subplot(2, 2, 1)
        data['cum_prob'].plot(kind='bar')
        xticks = ">= " + data['count'].astype('str') + data['cum_prob'].apply(lambda x: "(%.2f%%)" % (x * 100))
        plt.xticks(data.index, xticks, rotation=70)
        plt.ylabel("5 ★ Cum probability")

        plt.subplot(2, 2, 2)
        data['prob'].plot(kind='bar')
        xticks = data['count'].astype('str') + data['prob'].apply(lambda x: "(%.2f%%)" % (x * 100))
        plt.xticks(data.index, xticks, rotation=70)
        plt.ylabel("5 ★ Probability")

        dist = self.four_star_up_target_dist
   
        mean = dist.mean()
        data = dist.value_counts().sort_index(ascending=False)
        total = data.sum()
        data = pd.DataFrame({'count': data.index, 'prob': data / total, 'cum_prob': (data / total).cumsum()})
        data.reset_index(inplace=True, drop=True)

        plt.subplot(2, 2, 3)
        data['cum_prob'].plot(kind='bar')
        xticks = ">= " + data['count'].astype('str') + data['cum_prob'].apply(lambda x: "(%.2f%%)" % (x * 100))
        plt.xticks(data.index, xticks, rotation=70)
        plt.ylabel("4 ★ Cum probability")

        plt.subplot(2, 2, 4)
        data['prob'].plot(kind='bar')
        xticks = data['count'].astype('str') + data['prob'].apply(lambda x: "(%.2f%%)" % (x * 100))
        plt.xticks(data.index, xticks, rotation=70)
        plt.ylabel("4 ★ Probability")        

        _ = plt.suptitle('Up char hit distritution, 5 ★ mean=%.2f, 4 ★ mean=%.2f' % 
            (self.five_star_up_dist.mean(), self.four_star_up_target_dist.mean()))        

    
if __name__ == '__main__':
    import argparse
    cmd = argparse.ArgumentParser(description='Simulate Genshin Impact wish')
    cmd.add_argument('--num_wish', required=True, type=int)
    cmd.add_argument('--num_no_five_star', required=True, type=int)
    cmd.add_argument('--num_no_four_star', default=0, type=int)
    cmd.add_argument('--last_five_star_no_up', action='store_true')
    cmd.add_argument('--last_four_star_no_up', action='store_true')    
    cmd.add_argument('--num_sim', type=int, default = 10000)
    args = cmd.parse_args()

    l = Lottory(
        no_four_star_streak = args.num_no_four_star,
        no_five_star_streak = args.num_no_five_star,
        last_five_star_no_up = args.last_five_star_no_up,
        last_four_star_no_up = args.last_four_star_no_up,
    )
    up5_dist, up4_dist = l.monte_carlo(
        num_sim = args.num_sim,
        num_wishes = args.num_wish,
    )

    

    print("5 star up avg: ", up5_dist.mean())
    print("4 star target avg: ", up4_dist.mean())

    l.display()
    plt.show()

