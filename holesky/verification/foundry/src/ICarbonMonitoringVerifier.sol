// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

interface ICarbonMonitoringVerifier {

    // EVENTS
    event RequestPostProofFulfilled(
        bytes32 requestId,
        string indexed projectID,
        address indexed projectVerifier
    );

    event RequestCarbonDataFulfilled(
        bytes32 requestId,
        string indexed agbUnit,
        string indexed deforestationUnit,
        string indexed sequestrationUnit
    );

    // STRUCTS
    struct DispersalRequest {
        uint expectedTimeofDispersal;
        string projectID;
        string dispersalRequestID;
        string lastUpdatedHeadCID;
    }

    struct CarbonDataQuery {
        uint agb;
        uint deforestation;
        uint sequestration;
    }

    // FUNCTIONS
    function requestDisperseData(string calldata _cid) external;


    function fulfillDisperseData(
        bytes32 _requestId, 
        string memory _postProofID,
        string memory _lastUpdatedHeadCID
    ) external;


    function requestPostProof(string calldata _cid) external;


    function fulfillPostProof(bytes32 _requestId) external;


    function requestCarbonData(uint _date, string calldata _cid) external;


    function fulfillCarbonData(
        bytes32 _requestId,
        uint256 _agbData, 
        uint256 _defData, 
        uint256 _seqData, 
        string calldata _agbUnit, 
        string calldata _defUnit, 
        string calldata _seqUnit
    ) external;
}