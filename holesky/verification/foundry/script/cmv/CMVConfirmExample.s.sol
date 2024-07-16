// // // SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Script.sol";
import "forge-std/console.sol";


interface ICMV {

    struct DispersalRequest {
        uint expectedTimeofDispersal;
        string cid;
        string dispersalRequestID;
        string lastUpdatedHeadCID;
    }
    
    function dispersalRequests(
        string calldata _projectID
    ) external view returns (uint expectedTimeofDispersal, string memory cid, string memory dispersalRequestID, string memory lastUpdatedHeadCID);

    function requestConfirmData(string memory _projectID) external;
}


contract CMVConfirmExample is Script {

    function run() external {   
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        vm.startBroadcast(deployerPrivateKey);

        address cmv = 0x441F674463aa613C57b39C7eE7Ad343F3C1886a8;
        string memory projectName = "852-monitor";
        string memory userID = "carbon@verifier.com";
        string memory projectID = string(abi.encodePacked(projectName, ":", userID));

        ICMV carbonMonitoringVerifier = ICMV(cmv);
        (uint expectedTimeofDispersal, string memory cid, string memory dispersalRequestID, string memory lastUpdatedHeadCID) = carbonMonitoringVerifier.dispersalRequests(projectID);
        console.log("Source file CID: ", cid);
        console.log("Dispersal Request ETA: ", expectedTimeofDispersal);
        console.log("Dispersal Request ID: ", dispersalRequestID);
        console.log("Last Updated Head CID: ", lastUpdatedHeadCID);

        carbonMonitoringVerifier.requestConfirmData(projectID);
        vm.stopBroadcast();
    }
}