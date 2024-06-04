// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Script.sol";
import "forge-std/console.sol";
import "../src/BlobVerifier.sol";
import "../lib/eigenda/contracts/src/libraries/EigenDARollupUtils.sol";


contract DeployBlobVerifier is Script {

    function run() external {   
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        address owner = vm.envAddress("WALLET_ADDRESS");
        vm.startBroadcast(deployerPrivateKey);

        new BlobVerifier(owner);
        vm.stopBroadcast();
    }
}