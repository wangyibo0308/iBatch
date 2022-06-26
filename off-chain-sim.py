
import sys
import os
import web3
import numpy as np
import pandas as pd
from collections import defaultdict
from web3 import Web3
from solc import compile_source
import time
import json
import threading
from collections import defaultdict



def deplopyFrontend():
    source_code_file = "./dispatcher.sol"
    with open(source_code_file, 'r') as source_code:
        contract_source_code = source_code.read()
    compiled_sol = compile_source(contract_source_code)
    contract_interface = compiled_sol['<stdin>:' + 'batcher']
    # Instantiate and deploy contract
    frontend = w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])
    w3.eth.defaultAccount = w3.eth.accounts[0]
    tx_hash = frontend.constructor().transact()
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    frontend = w3.eth.contract(
        address=tx_receipt.contractAddress,
        abi=contract_interface['abi'],
    )
    return frontend


def deplopyERC20():
    source_code_file = "./ERC20Token.sol"
    with open(source_code_file, 'r') as source_code:
        contract_source_code = source_code.read()
    compiled_sol = compile_source(contract_source_code)
    contract_interface = compiled_sol['<stdin>:' + 'ERC20Token']
    # Instantiate and deploy contract
    w3.eth.defaultAccount = w3.eth.accounts[0]
    ERC20 = w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])
    tx_hash = ERC20.constructor(999999999000000000000000000, 'testToken', 1, 'tT').transact()
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    erc20 = w3.eth.contract(
        address=tx_receipt.contractAddress,
        abi=contract_interface['abi'],
    )
    return erc20

def generatemsg(contractlist,batchnonce):
    msg = Web3.solidityKeccak(['address[]','uint256'], [contractlist,batchnonce])
    return msg.hex()

if __name__ == "__main__":
    rpcURL_remote = "http://127.0.0.1:8545"
    w3 = Web3(Web3.HTTPProvider(rpcURL_remote))
    miner = w3.geth.miner
    miner.start(4)
    # read trace
    trace_path = "transfer_trace.csv"
    trace = pd.read_csv(trace_path)
    w3.eth.defaultAccount = w3.eth.accounts[0]
    erc20 = deplopyERC20()
    dispatcher = deplopyFrontend()
    miner.stop()

    gas_dict = {}
    col = trace['blockNumber']
    data = col.drop_duplicates()
    arrs = data.values
    for arr in arrs:
        gas_dict[arr] = None
    result_list = []
    k = 0
    batchnonce = 0
    for key in gas_dict:
        block_trace = trace.loc[(trace['blockNumber'] == key)]
        block_trace_length = len(block_trace)
        funcHashs = []
        argslist = []
        contractlist = []
        sigs = []
        priveKey_list = []
        for i in range(block_trace_length):
            current_call = block_trace.iloc[i]
            sender = current_call['sender']
            receiver = current_call['receiver']
            amount = int(current_call['amount'])
            funcHashs.append(current_call['function_hash'])
            sender = w3.toChecksumAddress(sender)
            priveKey_list.append(current_call['prive_key'])
            receiver = w3.toChecksumAddress(receiver)
            argslist.append([int(receiver,16),amount])
            contractlist.append(w3.toChecksumAddress(erc20.address))
        for i in range(len(contractlist)):
            HashMsg = generatemsg(contractlist,batchnonce)
            sig = w3.eth.account.signHash(HashMsg, private_key=priveKey_list[i])
            sigs.append(sig['signature'])
        if len(contractlist) != 0:
            txhash = dispatcher.functions.dispatch(contractlist, funcHashs,argslist, batchnonce,sigs).transact({'gasPrice': 10}).hex()
            gas_dict[key] = txhash
            batchnonce += 1
    print('start miner')
    miner.start(12)
    time.sleep(10)
    for key in gas_dict:
        batchprice = 0
        txhash = gas_dict[key]
        if txhash == None:
            continue
        rc = w3.eth.waitForTransactionReceipt(txhash)
        gasused = rc['gasUsed']
        result = [key, gasused]
        result_list.append(result)
    col = ['block', 'gas_Used']
    new_test = pd.DataFrame(columns=col, data=result_list)
    final_new = new_test.sort_values(by=['block'])
    name = "tokenBatchresult.csv"
    final_new.to_csv(name, encoding='utf-8', index=False)
    miner.stop()