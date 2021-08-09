//pragma solidity ^0.4.10;
pragma experimental ABIEncoderV2;
contract batcher{
    event GET(uint256, uint256, uint256, uint256, uint256, uint256, uint256);
    function verify(bytes32 msgHash, bytes sig) returns (address) {
        require(sig.length == 65);
        bytes32 r;
        bytes32 s;
        uint8 v;
        assembly {
            // first 32 bytes, after the length prefix
            r := mload(add(sig, 32))
            // second 32 bytes
            s := mload(add(sig, 64))
            // final byte (first byte of the next 32 bytes)
            v := byte(0, mload(add(sig, 96)))
        }
        return ecrecover(msgHash, v, r, s);
    }

    function dispatch(address[] contractaddress,  bytes32[] funcHashs, uint256[] arg1, uint256[] arg2, uint256 batchernonce, bytes[] sig) public {
        uint leng = contractaddress.length;
        address sender;
        bytes32 msgHash = keccak256(abi.encodePacked(contractaddress, funcHashs, arg1, arg2, batchernonce));
        for (uint i = 0; i<leng; i++){
            sender = verify(msgHash,sig[i]);
            contractaddress[i].call(bytes4(funcHashs[i]), uint256(sender), uint256(arg1[i]), uint256(arg2[i]));
        }
    }
}
