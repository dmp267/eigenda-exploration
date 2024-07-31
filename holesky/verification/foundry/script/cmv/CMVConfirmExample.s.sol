// // // SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Script.sol";
import "forge-std/console.sol";

import {Strings} from "../../lib/openzeppelin-contracts/contracts/utils/Strings.sol";

// import "../../src/interfaces/ICarbonMonitoringVerifier.sol";
// import "../../src/contracts/CarbonMonitoringVerifier.sol";

interface ICMV {

    struct UserProject {
        bool isSubscribed;
        uint8 projectState;
        uint start;
        uint end;
        uint expectedTimeofDispersal;
        uint expectedTimeofExpiry;
        string cid;
        string dispersalRequestID;
        string lastUpdatedHeadCID;
    }


    struct UserDetail {
        bool whitelisted;
        UserProject[] userProjects;
    }
    

    function userDetails(
        address _userAddress
    ) external view returns (UserDetail memory userDetail);


    function projectIndex(
        string memory _projectID
    ) external view returns (uint256);


    function requestConfirmData(address _user, string memory _projectID) external;
}


contract CMVConfirmExample is Script {

    function run() external {   
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        vm.startBroadcast(deployerPrivateKey);

        address cmv = 0x526E869A13Bc607C9cE057Db586A91d278A5D221;
        string memory projectName = "852-monitor";
        // string memory userID = "carbon@verifier.com";
        address userAddress = vm.envAddress("WALLET_ADDRESS");
        // string memory userID = Strings.toHexString(uint256(uint160(userAddress)), 20);
        // string memory projectID = string(abi.encodePacked(userID, ":", projectName));

        ICMV carbonMonitoringVerifier = ICMV(cmv);
        // (uint expectedTimeofDispersal, string memory cid, string memory dispersalRequestID, string memory lastUpdatedHeadCID) = carbonMonitoringVerifier.dispersalRequests(projectID);
        // ICMV.UserDetail memory userDetail = carbonMonitoringVerifier.userDetails(userAddress);
        // uint index = carbonMonitoringVerifier.projectIndex(projectID);
        // ICMV.UserProject memory userProject = userDetail.userProjects[index];
        // console.log("Source file CID: ", userProject.cid);
        // console.log("Dispersal Request ETA: ", userProject.expectedTimeofDispersal);
        // console.log("Dispersal Request ID: ", userProject.dispersalRequestID);
        // console.log("Last Updated Head CID: ", userProject.lastUpdatedHeadCID);

        carbonMonitoringVerifier.requestConfirmData(userAddress, projectName);
        vm.stopBroadcast();
    }
}