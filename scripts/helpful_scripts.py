from brownie import (
    network,
    accounts,
    config,
    MockV3Aggregator,
    Contract,
    VRFCoordinatorMock,
    LinkToken,
    interface,
)
from web3 import Web3

LOCAL_FORKED_ENVIORMENTS = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_DEPLOYMENT_ENVIORNMENTS = ["development", "ganache-local"]


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if (
        network.show_active() in LOCAL_DEPLOYMENT_ENVIORNMENTS
        or network.show_active() in LOCAL_FORKED_ENVIORMENTS
    ):
        return accounts[0]
    return accounts.add(config["wallets"]["from_key"])


DECIMALS = 8
STARTING_PRICE = 200_000_000_000


def deploy_mocks(decimals=DECIMALS, starting_price=STARTING_PRICE):
    account = get_account()
    MockV3Aggregator.deploy(decimals, starting_price, {"from": get_account()})
    link_token = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(link_token.address, {"from": account})
    print("Mocks deployed!")


contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}


def get_contract(contract_name):
    """
    This function will grab the cotract addresses from the brownie config if defined, otherwise it will deploy a mock version of that contract and return that mock contract.

        Args:
            contract_name (string) (E.g. 'eth_usd_price_feed')

        Returns:
            brownie.network.contract.ProjectContract: The most recently deployed version of this contract. (E.g. 'MockV3Aggregator')
    """
    contract_type = contract_to_mock[contract_name]  # E.g. MockV3Aggregator
    if network.show_active() in LOCAL_DEPLOYMENT_ENVIORNMENTS:
        if len(contract_type) <= 0:  # Not deployed yet
            # MockV3Aggregator.length
            deploy_mocks()
        contract = contract_type[-1]
        # MockV3Aggregator[-1]
    else:
        contract_address = config["networks"][network.show_active()].get(contract_name)
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
    return contract


def fund_with_link(
    contract_address, account=None, link_token=None, amount=250000000000000000
):  # 0.25 LINK
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    tx = link_token.transfer(contract_address, amount, {"from": account})
    # link_token_contract = interface.LinkTokenInterface(link_token.address)
    # tx = link_token_contract.transfer(contract_address, amount, {"from": account})
    tx.wait(1)
    print("Contract funded!")
    return tx
