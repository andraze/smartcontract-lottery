from scripts.deploy_lottery import deploy_lottery
from scripts.helpful_scripts import (
    LOCAL_DEPLOYMENT_ENVIORNMENTS,
    fund_with_link,
    get_account,
)
from brownie import network
import pytest
import time


def test_can_pick_winner():
    if network.show_active() in LOCAL_DEPLOYMENT_ENVIORNMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee() + 100})
    lottery.enter({"from": account, "value": lottery.getEntranceFee() + 100})
    fund_with_link(lottery)

    lottery.endLottery({"from": account})
    time.sleep(60)
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
