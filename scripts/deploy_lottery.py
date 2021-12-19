from brownie import config, network, Lottery
from scripts.helpful_scripts import get_account, get_contract, fund_with_link
from web3 import Web3
import time


def deploy_lottery():
    acc = get_account()
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": acc},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    print("Deployed Lottery!")
    return lottery


def start_lottery():
    acc = get_account()
    lottery = Lottery[-1]
    starting_txn = lottery.startLottery({"from": acc})
    starting_txn.wait(1)
    print("The Lottery has started!")


def enter_lottery():
    acc = get_account()
    lottery = Lottery[-1]
    value = lottery.getEntranceFee() + 100000000
    tx = lottery.enter({"from": acc, "value": value})
    tx.wait(1)
    print("You entered the Lottery!")


def end_lottery():
    acc = get_account()
    lottery = Lottery[-1]
    """
    In order to end the lottery, we need LINK token to run the VRF chainlink Randomness function.
    So, we need to fund the contract. Then, end the lottery. Function in helpful_scripts
    """
    tx = fund_with_link(lottery.address)
    tx.wait(1)
    ending_txn = lottery.endLottery({"from": acc})
    ending_txn.wait(1)
    time.sleep(60)
    print(f"{lottery.recentWinner()} is the new winner!")


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()
