// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

interface ICarbonMonitoringVerifier {

    // EVENTS
    event RequestConfirmDataFulfilled(
        bytes32 requestId,
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

    struct CarbonDataQuery {
        uint agb;
        uint deforestation;
        uint sequestration;
    }

    // FUNCTIONS
    function requestDisperseData(
        uint _start,
        uint _end,
        string calldata _projectID, 
        string calldata userID, 
        string calldata _cid
    ) external;


    function fulfillDisperseData(
        bytes32 _requestId, 
        string memory _postProofID,
        string memory _lastUpdatedHeadCID
    ) external;


    function requestConfirmData(string calldata _cid) external;


    function fulfillConfirmData(bytes32 _requestId) external;


    function requestRetrieveData(uint _date, string calldata _projectID) external;


    function fulfillRetrieveData(
        bytes32 _requestId,
        uint256 _agbData, 
        uint256 _defData, 
        uint256 _seqData, 
        string calldata _agbUnit, 
        string calldata _defUnit, 
        string calldata _seqUnit
    ) external;
}