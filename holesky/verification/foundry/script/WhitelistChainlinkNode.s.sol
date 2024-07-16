// // SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Script.sol";
import "forge-std/console.sol";

// import "../lib/chainlink/contracts/src/v0.8/interfaces/OperatorInterface.sol";
import "../lib/chainlink/contracts/src/v0.8/operatorforwarder/interfaces/IAuthorizedReceiver.sol";


contract Whitelister is Script {

    function run() external {   
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        vm.startBroadcast(deployerPrivateKey);

        IAuthorizedReceiver operator = IAuthorizedReceiver(0xCCda5E49Ff369640EdfA0fb58fb6AF165B53B8B5);

        address[] memory senders = new address[](1);
        senders[0] = 0x608690f1780179a4A60F3E65d41BC15140fFA4f6;
        
        operator.setAuthorizedSenders(senders);
        vm.stopBroadcast();
    }
}