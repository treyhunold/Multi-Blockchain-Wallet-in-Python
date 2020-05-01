import os
from constants import *
from web3 import Web3
from dotenv import load_dotenv
from web3.middleware import geth_poa_middleware
from web3.gas_strategies.time_based import medium_gas_price_strategy
from eth_account import Account
from bit import Key
from bit import PrivateKeyTestnet
from bit.network import NetworkAPI
import subprocess
import json

load_dotenv()
mnemonic = os.getenv('MNEMONIC', 'review duck utility honey bike discover friend fat trophy injury matter buffalo')

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
w3.eth.setGasPriceStrategy(medium_gas_price_strategy)

def derive_wallets(coin, mnemonic, depth):
    p = subprocess.Popen(
        f"./derive -g --mnemonic='{mnemonic}' --coin={coin} --numderive={depth} --format=json",
        stdout=subprocess.PIPE,
        shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    return json.loads(output)

def priv_key_to_account(coin,priv_key):

    if (coin==BTCTEST):
        return PrivateKeyTestnet(priv_key)
    else :
        return Account.privateKeyToAccount(priv_key)

def create_raw_tx(account, recipient, amount):
    gasEstimate = w3.eth.estimateGas(
        {"from": account.address, "to": recipient, "value": amount}
    )
    return {
        "from": account.address,
        "to": recipient,
        "value": amount,
        "gasPrice": w3.eth.gasPrice,
        "gas": gasEstimate,
        "nonce": w3.eth.getTransactionCount(account.address),
    }

def create_tx(coin, account, to, amount):
    if (coin==ETH):
        return create_raw_tx(account,to,amount)
    else:
        return PrivateKeyTestnet.prepare_transaction(account.address, [(to, amount, BTC)])

def send_tx(coin, account, recipient, amount):
    tx = create_tx(coin,account, recipient, amount)
    signed_tx = account.sign_transaction(tx)
    result=None
    if(coin==ETH):
        result = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    else:
        result=NetworkAPI.broadcast_tx_testnet(signed_tx)
    return result