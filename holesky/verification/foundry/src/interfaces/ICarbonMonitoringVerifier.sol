// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

interface ICarbonMonitoringVerifier {

    // EVENTS
    event RequestDisperseDataFulfilled(
        bytes32 requestId,
        string indexed dispersalRequestID,
        string indexed lastUpdatedHeadCID
    );

    event RequestConfirmDataFulfilled(
        bytes32 requestId,
        bool indexed confirmed,
        string indexed projectID,
        address indexed projectVerifier
    );

    // event RequestRetrieveDataFulfilled(
    //     bytes32 requestId,
    //     string indexed agbUnit,
    //     string indexed deforestationUnit,
    //     string indexed sequestrationUnit
    // );

    // STRUCTS
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


    struct JobRequest {
        address user;
        string projectID;
    }


    // struct CarbonDataQuery {
    //     uint agb;
    //     uint deforestation;
    //     uint sequestration;
    // }

    // FUNCTIONS
    function getUserDetail(address _user) external view returns (UserDetail memory);


    function setProjectVerifier(address _projectVerifier) external;


    function whitelistUser(address _user) external;


    function updateProjectState(address _user, string memory _projectName) external;


    function requestRedispersal(address _user, string memory _projectName) external;


    function requestInitialDispersal(
        bool _isSubscription,
        uint _start,
        uint _end,
        string memory _projectName,
        string memory _cid
    ) external;


    function fulfillDisperseData(
        bytes32 _requestId, 
        string memory _dispersalID,
        string memory _lastUpdatedHeadCID
    ) external;


    function requestConfirmData(address _user, string memory _projectName) external;


    function fulfillConfirmData(bytes32 _requestId, bool _isConfirmed) external;


    // function requestRetrieveData(uint _date, bytes32 _projectID) external;


    // function fulfillRetrieveData(
    //     bytes32 _requestId,
    //     uint256 _agbData, 
    //     uint256 _defData, 
    //     uint256 _seqData, 
    //     string calldata _agbUnit, 
    //     string calldata _defUnit, 
    //     string calldata _seqUnit
    // ) external;
}