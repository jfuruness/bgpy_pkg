class BGPSimplePolicyEx:
    def receive_ann(self):
        print("in BGPSimplePolicyEx")
        raise NotImplementedError


class BGPPolicyEx(BGPSimplePolicyEx):
    def receive_ann(self):
        print("in BGPPolicyEx")


class ASPASimplePolicyEx(BGPSimplePolicyEx):
    pass


class ASPAPolicy(ASPASimplePolicyEx, BGPPolicyEx):
    pass


if __name__ == "__main__":
    ASPAPolicy().receive_ann()
