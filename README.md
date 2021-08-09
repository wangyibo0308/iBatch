# iBatch
A Ethereum improvement proposal to enable secure batching of smart contract invocations against an untrusted relay server off-chain.

# System model

![alt text](https://github.com/wangyibo0308/iBatch/blob/main/image/system_model.png)

iBatch is a middleware system running on top of an operational Ethereum network to enable secure batching of smart contract invocations. We introduce two new intermediaries, untrusted Batcher off-chain and trusted dispatcher smart contract on-chain. The untrusted Batcher can mount attacks to forge, replay, modify and even omit the invocations from the callers. Also, the Batcher can refuse to batch invocations.

# Security Protocal

![alt text](https://github.com/wangyibo0308/iBatch/blob/main/image/security_protocol.png)

The security protocol achieves invocation integrity against malicious Batcher and prevents the Batcher from forging or replaying a caller’s invocation in a batch transaction. The key idea is reusing a tx-wise nonce to defend against the replays of all N invocations in the batch transaction. Suppose in a batch time window, there are N invocations submitted from different callers. The iBatch protocol follows the batching framework described above and it works in the following four steps: 
  * In the batch time window, a caller submits the 𝑖-th invocation request, denoted by call_i, to the Batcher service.
  * By the end of the batch time window, the Batcher prepares a batch message bmsg and sends it to the callers for validation and signing. The bmsg is a concatenation of the 𝑁 requests, call_i’s, their caller nonces nonce_i ’s, and Batcher account’s nonce, nonce_B. Each of the callers checks if there is one and only one copy of its invocation in the bmsg. After a successful check of equality, the caller signs the message bmsg_sign, that is, bmsg without callers’ nonces. She then sends her signature to the Batcher.
  * Batcher includes the signed message bmsg_sign in a transaction’s data field and sends the transaction, called batch transaction, to be received by the Dispatcher smart contract.
  * In function dispatch, smart contract Dispatcher parses the transaction and extracts the original invocations call_i before forwarding them to callees. Smart contract Dispatcher internally verifies the signature of each extracted invocation against its caller’s public key; this can be done by using Solidity function ecrecover(call𝑖,sig𝑖,account𝑖). If successful, the Dispatcher then internal-calls the callee smart contract. 

# Middleware systems

![alt text](https://github.com/wangyibo0308/iBatch/blob/main/image/middleware_system.png)

We build a middleware system on top of the underlying Ethereum-DApp ecosystem. The Batcher middleware runs on an Ethereum client (e.g., a Geth client), by extending its RPC components. The Dispatcher smart contract runs on the Ethereum network and forwards invocations to the callee smart contracts. A signer runs at Dapp client to check and sign the bmsg for supporting the security protocol. The instrumented Geth node unmarshals a raw transaction received and extracts its arguments, and places it in Batcher’s buffer. The Batcher makes essential decisions regarding which invocations to be included in the next batch transaction depends on the batching policy. The callee smart contract also needs to be rewritten to integrate iBatch.

# Integration with legacy smart_contract

Running iBatch with unmodified smart contracts on today’s Ethereum clients would fail because the unmodified smart contracts do not authorize the unmarshalled invocations sent from Dispatcher account. To support iBatch, callee smart contracts need to authenticate the internal calls from Dispatcher and this entails rewriting DApps’ smart contracts to whitelist the Dispatcher account. The following smart-contract code illustrates the example of rewriting transfer() in an ERC20 token contract. 

![alt text](https://github.com/wangyibo0308/iBatch/blob/main/image/rewritting_SC.png)

We notice a recent Ethereum Improvement Proposal EIP-3074, which is currently in progress, would make it possible to directly integrate iBatch with an operation Ethereum network without rewriting smart contracts.

# Control policies
We notice under different workloads, the most cost-effective policy may differ. We propose mechanisms and policies for our middleware system to properly batch invocations for optimizing cost and delay.
  * Batch all calls in a W-second window (codename: Wsec)
  * Batch only the calls from top-1 caller (Top1)
  * Batch only when there are more than X calls in the window (MinX)
  * Set the Gas price of batch tx to be higher P% of calls in the batch

# Summary
  * We design a security batching framework. it prevents the Batcher from forging or replaying a caller’s invocation in a batch transaction. It also ensures the Batcher’s attempt to omit a caller’s invocations can be detected by the victim caller. In addition, iBatch can be extended to prevent a denial-of-service caller from delaying a batch.
  * We propose mechanisms and policies for the Batcher to properly batch invocations for design goals in cost and delay.
  * The technical details are in our paper: https://tristartom.github.io/docs/fse21-ibatch.pdf
