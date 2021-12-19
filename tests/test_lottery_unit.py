# 1.3172 * 10 ** 16 -> current price of ethereum
from brownie import Lottery, accounts, network, config, exceptions
from scripts.deploy_lottery import deploy_lottery
from scripts.helpful_scripts import (
    get_account,
    LOCAL_BLOCKCHAIN_ENVI,
    fund_with_link,
    get_contract,
)
from web3 import Web3
import pytest


def test_get_entrance_fee():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVI:
        pytest.skip("only for local testing")
    # Arrange
    lottery = deploy_lottery()
    # Act
    # 2000 initial_value; USDentryfee is $50
    # 50/2000 is expected eth entrance value
    expected_entrance_fee = Web3.toWei(0.025, "ether")
    entrance_fee = lottery.getEntranceFee()
    # Assert
    assert expected_entrance_fee == entrance_fee


def test_cant_enter_unless_started():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVI:
        pytest.skip("only for local testing")
    lottery = deploy_lottery()
    # Act/Assert
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": get_account(), "value": lottery.getEntranceFee()})


def test_can_start_and_enter_lottery():
    # Arrange`
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVI:
        pytest.skip("only for local testing")
    lottery = deploy_lottery()
    acc = get_account()
    lottery.startLottery({"from": acc})
    # Act
    lottery.enter({"from": acc, "value": lottery.getEntranceFee()})
    # Assert
    assert lottery.players(0) == acc


def test_can_end_lottery():
    # Arrange`
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVI:
        pytest.skip("only for local testing")
    lottery = deploy_lottery()
    acc = get_account()
    lottery.startLottery({"from": acc})
    lottery.enter({"from": acc, "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    lottery.endLottery({"from": acc})
    assert (
        lottery.lottery_state() == 2
    )  # kucch khaas hai nahi isme check karne ko, bas lottery state hi hai.


def test_can_pick_winner_correctly():
    # Arrange`
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVI:
        pytest.skip("only for local testing")
    lottery = deploy_lottery()
    acc = get_account()
    lottery.startLottery({"from": acc})
    lottery.enter({"from": acc, "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=2), "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=3), "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    starting_balance_0f_account = acc.balance()
    balance_of_lottery = lottery.balance()
    txn = lottery.endLottery({"from": acc})
    request_id = txn.events["RequestedRandomness"]["requestID"]
    STATIC_RNG = 777
    get_contract("vrf_coordinator").callBackWithRandomness(
        request_id, STATIC_RNG, lottery.address, {"from": acc}
    )

    # 777%3 = 0 -> Winner -> 0

    assert lottery.recentWinner() == acc
    assert lottery.balance() == 0
    assert acc.balance == starting_balance_0f_account + balance_of_lottery
