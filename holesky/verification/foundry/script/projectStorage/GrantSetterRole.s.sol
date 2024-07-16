// // SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Script.sol";
import "forge-std/console.sol";
import "../../src/IProjectStorageVerifier.sol";


contract GrantSetterRole is Script {
    function run() external {   
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        address owner = vm.envAddress("WALLET_ADDRESS");
        address verifier = 0x8032b4DBa3779B6836B4C69203bB1d3b4f92908B;
        vm.startBroadcast(deployerPrivateKey);

        IProjectStorageVerifier projectStorageVerifier = IProjectStorageVerifier(verifier);

        projectStorageVerifier.grantSetterRole(owner);
        vm.stopBroadcast();
    }
}
