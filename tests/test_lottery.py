from brownie import Lottery, accounts, config, network
from scripts.helpful_scripts import get_account
from web3 import Web3


# Trenutna cena eth je cca 2500 -> 50 / 2500 = 0.019


def test_get_entrance_fee():
    my_account = get_account()
    lottery = Lottery.deploy(
        config["networks"][network.show_active()]["eth_usd_price_feed"],
        {"from": my_account},
    )
    assert lottery.getEntranceFee() > Web3.toWei(0.018, "ether")
    assert lottery.getEntranceFee() < Web3.toWei(0.022, "ether")
