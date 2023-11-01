import web3
from web3 import Web3, HTTPProvider
import json
import csv
import random
import time
import os
from dotenv import load_dotenv
from web3.exceptions import TimeExhausted
import requests

load_dotenv()
# 读取JSON数据
with open("abi/scroll_test_abi.json", "r") as f:
    testabi = json.load(f)

RPC = os.getenv("goerli_key")
web3 = Web3(
    Web3.HTTPProvider(RPC))
print(web3.is_connected())

def runtestcontractabi(account, privatekey, _gasLimit):
    a = random.uniform(0.002, 0.01)
    _amount = int(a * 10**18)
   
    testcontractaddress = web3.to_checksum_address(
        "0xe5E30E7c24e4dFcb281A682562E53154C15D3332"
    )
    contract = web3.eth.contract(address=testcontractaddress, abi=testabi)

    nonce = web3.eth.get_transaction_count(account)
    transaction = contract.functions.depositETH(_amount, _gasLimit).build_transaction(
        {
            "nonce": nonce,
            "gas": 350000,
            "gasPrice": web3.eth.gas_price,
            "value": web3.to_wei(a + 0.0001, "ether"),
        }
    )

    signedTx = web3.eth.account.sign_transaction(transaction, privatekey)
    txhash = web3.eth.send_raw_transaction(signedTx.rawTransaction)

    print("Transaction hash:", txhash.hex())

    # 检查交易状态
    try:
        txreceipt = web3.eth.wait_for_transaction_receipt(txhash, timeout=2)
        if txreceipt["status"] == 1:
            print("Transaction succeeded")
            print("Transaction status:", txreceipt["status"])
            return True
        else:
            print("Transaction failed")
            print("Transaction status:", txreceipt["status"])
            return False
    except TimeExhausted:
        print("Transaction is pending after 2 seconds")
        return False
    except requests.exceptions.SSLError as e:
        print(f"SSL Error encountered: {e}. Skipping to the next account.")
        return False

# 遍历读取csv文件
with open("wallet.csv", "r") as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        account, privatekey = row
        # 提供gas限制来运行这个函数
        transaction_success = runtestcontractabi(account, privatekey, _gasLimit=50000)
        if not transaction_success:
            print("Skipping to next account due to transaction failure or timeout.")
        time.sleep(random.uniform(1, 2))
