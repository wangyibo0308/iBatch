pragma experimental ABIEncoderV2;
contract batcher{
    event GET(uint256, uint256, uint256, uint256, uint256, uint256, uint256);
    function verify(bytes32 msgHash, bytes memory sig) public returns (address) {
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

   function dispatch(address[] memory contractAddrs, bytes32[] memory funcHashs, uint256[][] memory args, uint256 batchernonce, bytes[] memory sigs) public{
        address msgSender;
        uint argsLen;
        bytes32 msgHash = keccak256(abi.encodePacked(contractAddrs,batchernonce));
        for(uint i=0; i<contractAddrs.length; i++){
            argsLen = args[i].length;
            if(argsLen == 1){
                msgSender = verify(msgHash,sigs[i]);
                contractAddrs[i].call(bytes4(funcHashs[i]), uint256(msgSender),args[i][0]);
            }
       
            if(argsLen == 2){
                msgSender = verify(msgHash,sigs[i]);
                contractAddrs[i].call(bytes4(funcHashs[i]),uint256(msgSender),args[i][0],args[i][1]);
            }
       
            if(argsLen == 3){
                msgSender = verify(msgHash,sigs[i]);
                contractAddrs[i].call(bytes4(funcHashs[i]),uint256(msgSender),args[i][0],args[i][1],args[i][2]);
            }
       
            if(argsLen == 4){
                msgSender = verify(msgHash,sigs[i]);
                contractAddrs[i].call(bytes4(funcHashs[i]),uint256(msgSender),args[i][0],args[i][1],args[i][2], args[i][3]);
            }
        }
        
    }
}
