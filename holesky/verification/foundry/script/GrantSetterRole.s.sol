// // SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Script.sol";
import "forge-std/console.sol";
import "../src/IProjectStorageVerifier.sol";


contract GrantSetterRole is Script {
    function run() external {   
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        address owner = vm.envAddress("WALLET_ADDRESS");
        address verifier = vm.envAddress("VERIFIER_CONTRACT_ADDRESS");
        vm.startBroadcast(deployerPrivateKey);

        IProjectStorageVerifier projectStorageVerifier = IProjectStorageVerifier(verifier);

        address setter = vm.envAddress("SETTER_ADDRESS");
        projectStorageVerifier.grantSetterRole(setter);
        projectStorageVerifier.grantSetterRole(owner);
        vm.stopBroadcast();
    }
}
