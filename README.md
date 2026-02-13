# iBatch
An Ethereum improvement proposal to enable secure batching of smart contract invocations against an untrusted relay server off-chain.

# System model

![alt text](https://github.com/wangyibo0308/iBatch/blob/main/image/system_model.png)

iBatch is a middleware system running on top of an operational Ethereum network to enable secure batching of smart contract invocations. We introduce two new intermediaries, an untrusted Batcher off-chain and a trusted dispatcher smart contract on-chain. The untrusted Batcher can mount attacks to forge, replay, modify and even omit the invocations from the callers. Also, the Batcher can refuse to batch invocations.

# Off-chain simulator
We are not ready to upload our Ethereum client that hooked with iBatch protocol at this time. We upload an off-chain simulator written with Python just to illustrate the off-chain batch process and how to interact with the dispatcher smart contract. This off-chain simulator shows a simple example that batching all the ERC-20 transfer invocations that are sent in the same block.

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
