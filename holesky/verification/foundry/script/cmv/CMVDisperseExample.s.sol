// // SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Script.sol";
import "forge-std/console.sol";

import "../../src/interfaces/ICarbonMonitoringVerifier.sol";
import "../../src/contracts/CarbonMonitoringVerifier.sol";


// interface ICMV {

//     struct UserProject {
//         bool isSubscribed;
//         uint8 projectState;
//         uint start;
//         uint end;
//         uint expectedTimeofDispersal;
//         uint expectedTimeofExpiry;
//         string cid;
//         string dispersalRequestID;
//         string lastUpdatedHeadCID;
//     }


//     struct UserDetail {
//         bool whitelisted;
//         UserProject[] userProjects;
//     }
    

//     struct JobRequest {
//         address user;
//         string projectID;
//     }


//     struct TestResult {
//         address user;
//         bytes32 requestId;
//         uint index;
//         string projectID;
//     }


//     function userDetails(
//         address _userAddress
//     ) external view returns (UserDetail memory userDetail);


//     function projectIndex(
//         string memory _projectID
//     ) external view returns (uint256);


//     function whitelistUser(address _userID) external;


//     function requestDisperseData(
//         bool _isSubscription,
//         uint _start,
//         uint _end,
//         string memory _projectID,
//         string memory _cid
//     ) external;


//     function testResult() external view returns (TestResult memory result);


//     function fulfillDisperseData(
//         bytes32 _requestId, 
//         string memory _dispersalID,
//         string memory _lastUpdatedHeadCID
//     ) external;
// }


contract CMVDisperseExample is Script {

    function run() external {   
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        vm.startBroadcast(deployerPrivateKey);
        CarbonMonitoringVerifier cmvContract = new CarbonMonitoringVerifier();
        address cmv = address(cmvContract);
        // ICarbonMonitoringVerifier cmvI = ICarbonMonitoringVerifier(cmv);
        // address cmv = 0x2b67793f764927c43014d00427Da5ea57f28d76E;
        uint start = 1514696400;
        uint end = 1703998800;
        string memory projectName = "852-monitor";
        // string memory userID = "carbon@verifier.com";
        address userAddress = vm.envAddress("WALLET_ADDRESS");
        string memory cid = "QmNdW3jkAgGLsAzeqHcrMHAoeCq6YpZyQqnG4ZLkXoSybb";
        ICarbonMonitoringVerifier carbonMonitoringVerifier = ICarbonMonitoringVerifier(cmv);

        carbonMonitoringVerifier.whitelistUser(userAddress);
        carbonMonitoringVerifier.requestDisperseData(
            true,
            start,
            end,
            projectName,
            cid
        );
        // ICMV.UserDetail memory test = cmvI.userDetails(userAddress);
        // uint len = test.userProjects.length;
        // console.log("User Projects Length: ", len);
        // uint reqid = 45855687203501119947128763494442806126910109964479197263239585159165834966582;
        // carbonMonitoringVerifier.fulfillDisperseData(
        //     bytes32(reqid),
        //     "173342183bb06fa6fe2576b534b3f8c2156713f51c4e465fe9c1efcc86923dd7-313732323434313032323236303433383038372f302f33332f312f33332fe3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        //     "bafyreifuh56spzd6rpn3yldxcrfibcjducrjm7ikmbf62s6c3txfpm366m"
        
        // );

        // ICarbonMonitoringVerifier.TestInput memory testInput = carbonMonitoringVerifier.readTestInput();
        // ICarbonMonitoringVerifier.TestOutput memory testOutput = carbonMonitoringVerifier.readTestOutput();

        // console.log("input Address: ", testInput.user);
        // console.log("input Index: ", testInput.index);
        // console.log("input Project ID: ", testInput.projectID);
        
        // console.log("output Address: ", testOutput.user);
        // console.log("output Index: ", testOutput.index);
        // console.log("output Project ID: ", testOutput.projectID);

        // ICMV.TestResult memory result = cmvI.testResult();
        // console.log("User Address: ", result.user);
        // console.log("Request ID: ", uint256(result.requestId));
        // console.log("Index: ", result.index);
        // console.log("Project ID: ", result.projectID);
        vm.stopBroadcast();
    }
}