// // SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Script.sol";
import "forge-std/console.sol";
import "../../src/ICarbonMonitoringVerifier.sol";


contract ChangeProjectStorageVerifier is Script {
    function run() external {   
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");

        address newVerifier = 0x8032b4DBa3779B6836B4C69203bB1d3b4f92908B;
        address cmv = 0x84F961bd58E752448ca660D2391fAd4e4E09A95E;
        vm.startBroadcast(deployerPrivateKey);

        ICarbonMonitoringVerifier carbonMonitoringVerifier = ICarbonMonitoringVerifier(cmv);

        carbonMonitoringVerifier.setProjectVerifier(newVerifier);

        vm.stopBroadcast();
    }
}
