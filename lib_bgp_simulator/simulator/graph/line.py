from math import sqrt
from statistics import mean, stdev


class Line:
    def __init__(self, policy, adopting, label):
        self.x = []
        self.y = []
        self.yerr = []
        self.label = label
        self.policy = policy
        self.adopting = adopting

    def add_data(self,
                 percent_adoption,
                 list_of_scenarios,
                 subg_name,
                 outcome,
                 policy):
        list_of_percents = [
            x.outcome_policy_percentages[subg_name][outcome][policy]
            for x in list_of_scenarios]
        self.x.append(percent_adoption)
        self.y.append(mean(list_of_percents))
        if len(list_of_percents) > 1:
            yerr_num = 1.645 * 2 * stdev(list_of_percents)
            yerr_denom = sqrt(len(list_of_percents))
            self.yerr.append(yerr_num / yerr_denom)
        else:
            self.yerr.append(0)
