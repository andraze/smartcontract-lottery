import pytest
from brownie import Lottery, accounts, config, network, exceptions
from scripts.helpful_scripts import (
    LOCAL_DEPLOYMENT_ENVIORNMENTS,
    fund_with_link,
    get_account,
    get_contract,
)
from web3 import Web3
from scripts.deploy_lottery import deploy_lottery


# Trenutna cena eth je cca 2500 -> 50 / 2500 = 0.019


def test_get_entrance_fee():
    if network.show_active() not in LOCAL_DEPLOYMENT_ENVIORNMENTS:
        pytest.skip()
    # Priprava
    myLottery = deploy_lottery()
    # Izvedba
    # 2,000 eth / usd
    # usdEntryFee = 50
    # 2000/1 == 50 / x == 0.025
    expected_entracne_fee = Web3.toWei(0.025, "ether")
    entrance_fee = myLottery.getEntranceFee()
    # Pogoj
    assert expected_entracne_fee == entrance_fee


def test_cant_enter_unless_started():
    if network.show_active() not in LOCAL_DEPLOYMENT_ENVIORNMENTS:
        pytest.skip()
    # Priprava
    lottery = deploy_lottery()
    # Izvedba in pogoj
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": get_account(), "value": lottery.getEntranceFee()})


def test_can_start_and_enter_lottery():
    if network.show_active() not in LOCAL_DEPLOYMENT_ENVIORNMENTS:
        pytest.skip()
    # Priprava
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    # Izvedba
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    # Pogoj
    assert lottery.players(0) == account


def test_can_end_lottery():
    if network.show_active() not in LOCAL_DEPLOYMENT_ENVIORNMENTS:
        pytest.skip()
    # Priprava
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    # Izvedba
    lottery.endLottery({"from": account})
    # Pogoj
    assert lottery.lottery_state() == 2


def test_can_pick_winner_correctly():
    if network.show_active() not in LOCAL_DEPLOYMENT_ENVIORNMENTS:
        pytest.skip()
    # Priprava
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=1), "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=2), "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    starting_balance_of_account = account.balance()
    balance_of_lottery = lottery.balance()
    end_transaction = lottery.endLottery({"from": account})
    request_id = end_transaction.events["requestedRandomness"]["requestId"]
    STATIC_RNG = 777
    get_contract("vrf_coordinator").callBackWithRandomness(
        request_id, STATIC_RNG, lottery.address, {"from": account}
    )
    # 777 % 3 = 0
    # Pogoj
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
    assert account.balance() == starting_balance_of_account + balance_of_lottery
