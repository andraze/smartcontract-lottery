from scripts.helpful_scripts import (
    LOCAL_DEPLOYMENT_ENVIORNMENTS,
    LOCAL_FORKED_ENVIORMENTS,
    get_account,
    get_contract,
    fund_with_link,
)
from brownie import config, Lottery, network
import time


def deploy_lottery():
    account = get_account()
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()].get("fee"),
        config["networks"][network.show_active()].get("keyhash"),
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    print("Deployed lottery!")
    return lottery


def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    starting_tx = lottery.startLottery({"from": account})
    starting_tx.wait(1)
    print("Lottery is started!")


def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    value = lottery.getEntranceFee()
    tx = lottery.enter({"from": account, "value": value})
    tx.wait(1)
    print("You entered the lottery!")


def end_lottery():
    account = get_account()
    lottery = Lottery[-1]
    # Fund the contract
    # End the lottery
    tx = fund_with_link(lottery.address)
    tx.wait(1)
    ending_tx = lottery.endLottery({"from": account})
    ending_tx.wait(1)
    # Wait for randomness (oracle node) to respond.
    time.sleep(120)
    print(f"{lottery.recentWinner()} is the WINNER!")


def main():
    if network.show_active() in LOCAL_DEPLOYMENT_ENVIORNMENTS:
        lottery = deploy_lottery()
        account = get_account()
        lottery.startLottery({"from": account})
        lottery.enter({"from": account, "value": lottery.getEntranceFee()})
        fund_with_link(lottery)
        end_transaction = lottery.endLottery({"from": account})
        request_id = end_transaction.events["requestedRandomness"]["requestId"]
        STATIC_RNG = 777
        get_contract("vrf_coordinator").callBackWithRandomness(
            request_id, STATIC_RNG, lottery.address, {"from": account}
        )
        print(f"Participant :{account}")
        print(f"Recent winner :{lottery.recentWinner()}")
    else:
        deploy_lottery()
        start_lottery()
        enter_lottery()
        end_lottery()
