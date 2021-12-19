from brownie import (
    accounts,
    config,
    network,
    MockV3Aggregator,
    VRFCoordinatorMock,
    LinkToken,
    Contract,
    interface,
)
from web3 import Web3

FORKED_LOCAL_ENVI = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVI = ["development", "ganache-local"]


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVI
        or network.show_active() in FORKED_LOCAL_ENVI
    ):
        return accounts[0]
    return accounts.add(config["wallets"]["from_key"])


contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}

DECIMALS = 8
INITIAL_VALUE = 200000000000


def deploy_mocks(decimals=DECIMALS, initial_value=INITIAL_VALUE):
    account = get_account()

    print(f"The active network is {network.show_active()}")
    print("Deploying mocks...")
    MockV3Aggregator.deploy(decimals, initial_value, {"from": account})
    link_token = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(link_token.address, {"from": account})
    print("Deployed Mocks!")


def fund_with_link(
    contract_address, account=None, link_token=None, amount=100000000000000000
):  # 0.1 LINK
    # we will use the account/link_token provided in the function arguments.
    # If nothing provided, we will use the default ones.
    acc = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    txn = link_token.transfer(contract_address, amount, {"from": acc})  # first method

    # another way of making contracts -> second method :-

    # link_token_contract = interface.LinkTokenInterface(link_token.address)
    # txn = link_token_contract.transfer(contract_address, amount, {"from": acc})
    txn.wait(1)
    print("Funded contract with LINK!")
    return txn


def get_contract(contract_name):
    """This function will grab the contract addresses from the brownie-config.yaml
    if defined, otherwise, it will deploy a mock version of that contract,
    and return that mock contract.

        Args:
            contract_name(str)

        Returns:
            brownie.network.contract.ProjectContract : The most recently deployed version of this contract.
            For Ex. -> MockV3Aggregator[-1]
    """
    contract_type = contract_to_mock[contract_name]

    if network.show_active() in LOCAL_BLOCKCHAIN_ENVI:
        if len(contract_type) <= 0:
            # above is equivalent to len(MockV3Aggregator)
            deploy_mocks()
        contract = contract_type[-1]
        # MockV3Aggregator[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        # address, ABI -> we have the ABI from MockV3Aggregator and the address is contract_address
        # another way of making contracts. MockV3Aggregator.abi
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
    return contract
