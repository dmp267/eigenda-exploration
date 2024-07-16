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

    event RequestRetrieveDataFulfilled(
        bytes32 requestId,
        string indexed agbUnit,
        string indexed deforestationUnit,
        string indexed sequestrationUnit
    );

    // STRUCTS
    struct DispersalRequest {
        uint expectedTimeofDispersal;
        string cid;
        string dispersalRequestID;
        string lastUpdatedHeadCID;
    }

    // struct CarbonDataQuery {
    //     uint agb;
    //     uint deforestation;
    //     uint sequestration;
    // }

    // FUNCTIONS
    function setProjectVerifier(address _projectVerifier) external;


    function requestDisperseData(
        uint _start,
        uint _end,
        string calldata _projectName,
        string calldata userID, 
        string calldata _cid
    ) external;


    function fulfillDisperseData(
        bytes32 _requestId, 
        string memory _projectID,
        string memory _dispersalRequestID,
        string memory _lastUpdatedHeadCID
    ) external;


    function requestConfirmData(string memory _projectID) external;


    function fulfillConfirmData(bytes32 _requestId, bool _isConfirmed, string memory _projectID) external;


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