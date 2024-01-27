class BGPSimplePolicyEx:
    def propagate(self):
        print("in BGPSimplePolicyEx")

    def valid_ann(self):
        print("in BGPSimplePolicyEx")


class BGPPolicyEx(BGPSimplePolicyEx):
    def propagate(self):
        print("in BGPPolicyEx")


class ROVSimplePolicyEx(BGPSimplePolicyEx):
    def valid_ann(self):
        print("in ROVSimplePolicyEx")


class ROVPolicy(ROVSimplePolicyEx, BGPPolicyEx):
    pass


if __name__ == "__main__":
    ROVPolicy().propagate()
    ROVPolicy().valid_ann()
