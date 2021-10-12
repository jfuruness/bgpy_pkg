#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This file contains system tests for the extrapolator pertaining to withdrawls.

For speciifics on each test, see the docstrings under each function.
"""
import pytest

from lib_caida_collector import PeerLink, CustomerProviderLink as CPLink

from ..utils import run_example, HijackLocalRib

from ...easy_ann import EasyAnn

from ....enums import Prefixes, ASNs, Relationships as Rels, ROAValidity
from ....announcement import Announcement
from ....simulator.attacks import PrefixHijack

from ....engine import BGPAS
from ....engine import ROVAS
from ....engine import BGPRIBsAS
from ....engine import LocalRib

__author__ = "Cameron Morris"
__credits__ = ["Cameron Morris", "Reynaldo Morillo"]
__Lisence__ = "BSD"
__maintainer__ = "Justin Furuness"
__email__ = "jfuruness@gmail.com"
__status__ = "Development"



#######################################
# Constants
#######################################

prefix = Prefixes.PREFIX.value 

kwargs = {"prefix": prefix, 
          "timestamp": 0, 
          "roa_validity": ROAValidity.UNKNOWN,
          "traceback_end": False}

#######################################
# Tests
#######################################


class Test_Withdraw:
    """Tests all example graphs within our paper."""

    #@pytest.mark.skip(reason="being converted")
    def test_simple_withdraw(self):
        r"""Simple test case for withdrawals.

                   1--2
                  /|\
                 3 4 5 
                   |  \
                   6   7
        """ 
        exr_output = {
            1: {prefix: EasyAnn(as_path=(1, 3), recv_relationship=Rels.CUSTOMERS, **kwargs)},
            2: {prefix: EasyAnn(as_path=(2, 1, 3), recv_relationship=Rels.PEERS, **kwargs)},
            3: {prefix: EasyAnn(as_path=(3,), recv_relationship=Rels.ORIGIN, **kwargs)},
            4: {prefix: EasyAnn(as_path=(4, 1, 3), recv_relationship=Rels.PROVIDERS, **kwargs)},
            5: {prefix: EasyAnn(as_path=(5, 7), recv_relationship=Rels.CUSTOMERS, **kwargs)},
            6: {prefix: EasyAnn(as_path=(6, 4, 1, 3), recv_relationship=Rels.PROVIDERS, **kwargs)},
            7: {prefix: EasyAnn(as_path=(7,), recv_relationship=Rels.ORIGIN, **kwargs)}
        }
        #exr_output = [{"asn": 1,
        #               "prefix": Attack.default_prefix,
        #               "origin": 3,
        #               "received_from_asn": 3},
        #              {"asn": 2,
        #               "prefix": Attack.default_prefix,
        #               "origin": 3,
        #               "received_from_asn": 1},
        #              {"asn": 3,
        #               "prefix": Attack.default_prefix,
        #               "origin": 3,
        #               "received_from_asn": Conds.HIJACKED.value},
        #              {"asn": 5,
        #               "prefix": Attack.default_prefix,
        #               "origin": 7,
        #               "received_from_asn": 7},
        #              {"asn": 7,
        #               "prefix": Attack.default_prefix,
        #               "origin": 7,
        #               "received_from_asn": Conds.NOTHIJACKED.value}]
        self._withdraw_check(ROVAS, exr_output)


####################
### Helper Funcs ###
####################

    def _withdraw_check(self, adopt_pol, exr_output):
        r"""Simple test case for withdrawals.
        Attacker is ASN 3 (... positioned where ASN 3 is [actual ASN is 3])
        Victim is ASN 7 (... positioned where ASN 7 is [actual ASN is 7])

                   1--2
                  /|\
                 3 4 5 
                   |  \
                   6   7
        """ 

        attack_type = PrefixHijack()
        peer_rows = [[1,2]]
        provider_customer_rows = [[1, 3],
                                  [1, 4],
                                  [1, 5],
                                  [4, 6],
                                  [5, 7]] 
        customer_providers = [CPLink(provider_asn=x[0], customer_asn=x[1]) for x in provider_customer_rows]
        peers = [PeerLink(x[0], x[1]) for x in peer_rows]

        # TODO : Review: Do we still need this comment?
        # One problem with double-propagation is  that since the victim
        # propagates first, the victim's announcement will get withdrawn. In
        # the past, this would be done by overwriting the old announcement, but
        # if 4 adopts, then 6 will not get the overwritten announcement.
        # Withdrawals solve this.

        bgp_ases = [1, 2, 3, 5, 6, 7]
        adopting_ases = [4]
        as_policies = dict()
        for bgp_as in bgp_ases:
            as_policies[bgp_as] = BGPAS
        for adopting_as in adopting_ases:
            as_policies[adopting_as] = adopt_pol

        announcements = [EasyAnn(prefix=prefix, as_path=(3,),timestamp=0, seed_asn=3,
                                 roa_validity=ROAValidity.UNKNOWN,
                                 recv_relationship=Rels.ORIGIN,
                                 traceback_end=True),
                         EasyAnn(prefix=prefix, as_path=(7,),timestamp=0, seed_asn=7,
                                 roa_validity=ROAValidity.UNKNOWN,
                                 recv_relationship=Rels.ORIGIN,
                                 traceback_end=True)]

 
        run_example(peers=peers,
                    customer_providers=customer_providers,
                    as_policies=as_policies,
                    announcements=announcements,
                    local_ribs=exr_output)
