// // SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Script.sol";
import "forge-std/console.sol";

import "../../src/interfaces/ICarbonMonitoringVerifier.sol";
import "../../src/contracts/CarbonMonitoringVerifier.sol";


contract CMVDisperseExample is Script {

    function run() external {   
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        vm.startBroadcast(deployerPrivateKey);
        // CarbonMonitoringVerifier cmvContract = new CarbonMonitoringVerifier();
        // address cmv = address(cmvContract);
        address cmv = 0x441F674463aa613C57b39C7eE7Ad343F3C1886a8;
        uint start = 1514696400;
        uint end = 1703998800;
        string memory projectName = "852-monitor";
        string memory userID = "carbon@verifier.com";
        string memory cid = "QmNdW3jkAgGLsAzeqHcrMHAoeCq6YpZyQqnG4ZLkXoSybb";

        ICarbonMonitoringVerifier carbonMonitoringVerifier = ICarbonMonitoringVerifier(cmv);
        carbonMonitoringVerifier.requestDisperseData(
            start,
            end,
            projectName,
            userID,
            cid
        );
        vm.stopBroadcast();
    }
}