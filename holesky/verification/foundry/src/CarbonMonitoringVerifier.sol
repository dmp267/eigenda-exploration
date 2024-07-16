// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {Chainlink, ChainlinkClient} from "../lib/chainlink/contracts/src/v0.8/ChainlinkClient.sol";
import {ConfirmedOwner} from "../lib/chainlink/contracts/src/v0.8/shared/access/ConfirmedOwner.sol";
import {LinkTokenInterface} from "../lib/chainlink/contracts/src/v0.8/shared/interfaces/LinkTokenInterface.sol";

import "./ICarbonMonitoringVerifier.sol";
import "./IProjectStorageVerifier.sol";

/**
 * THIS IS AN EXAMPLE CONTRACT THAT USES UN-AUDITED CODE.
 * DO NOT USE THIS CODE IN PRODUCTION.
 */

contract CarbonMonitoringVerifier is
    ICarbonMonitoringVerifier,
    ChainlinkClient,
    ConfirmedOwner
{
    using Chainlink for Chainlink.Request;

    uint256 private constant ORACLE_PAYMENT = (0 * LINK_DIVISIBILITY) / 10; // 0.0 * 10**18
    address constant LINK_ADDRESS = 0xd27376e609bF32b506535efe2bf1303a74Eb5467; // <- Holesky
    address constant OPERATOR_ADDRESS = 0xCCda5E49Ff369640EdfA0fb58fb6AF165B53B8B5; // <- Holesky
    bytes32 constant DISPERSAL_JOB_ID = "eaf2170545dc4793aadd19aa3dc82d66"; // <- Holesky
    bytes32 constant CONFIRM_JOB_ID = "8808538aeb2d4309a33af1edc9feb452"; // <- Holesky
    bytes32 constant DATA_JOB_ID = "fb8dbec0c82b45bda79f0edb5b693872"; // <- Holesky

    address public projectVerifier = 0x8032b4DBa3779B6836B4C69203bB1d3b4f92908B;
    mapping(string => DispersalRequest) public dispersalRequests;
    // mapping(bytes32 => CarbonDataQuery) public carbonDataQueries;

    mapping(string => uint8) public projectStates; //0: not initialized, 1: dispersal requested, 2: data confirmed, 3: data expired
    mapping(string => string[]) public userProjects;


    constructor() ConfirmedOwner(msg.sender) {
        _setChainlinkToken(LINK_ADDRESS);
    }

    /**
     * 
     * @param _projectVerifier address of ProjectStorageVerifier contract
     */
    function setProjectVerifier(address _projectVerifier) public onlyOwner {
        projectVerifier = _projectVerifier;
    }

    /**
     * 
     * @param _start timestamp in 's' of start of desired range
     * @param _end timestamp in 's' of end of desired range
     * @param _projectName user-defined name of project, must not conflict with other projects by the same user
     * @param _userID unique ID of user
     * @param _cid CID of uploaded KML file on IPFS
     */
    function requestDisperseData(
        uint _start,
        uint _end,
        string calldata _projectName,
        string calldata _userID,
        string calldata _cid
    ) public onlyOwner {
        Chainlink.Request memory req = _buildOperatorRequest(
            DISPERSAL_JOB_ID,
            this.fulfillDisperseData.selector
        );

        string memory _projectID = string(abi.encodePacked(_projectName, ":", _userID));
        req._add("projectID", _projectID);
        req._add("cid", _cid);
        req._addUint("start", _start);
        req._addUint("end", _end);

        _sendChainlinkRequestTo(OPERATOR_ADDRESS, req, ORACLE_PAYMENT);
        if (projectStates[_projectID] == 0) {
            userProjects[_userID].push(_projectName);
            projectStates[_projectID] = 1;
        } 
        projectStates[_projectID] = 1;
        dispersalRequests[_projectID].cid = _cid;
    }

    /**
     * 
     * @param _requestId ID for Chainlink job request
     * @param _dispersalID ID for EigenDA dispersal request
     * @param _lastUpdatedHeadCID most recent IPFS head CID for associated datasets
     */
    function fulfillDisperseData(
        bytes32 _requestId,
        string memory _projectID,
        string memory _dispersalID,
        string memory _lastUpdatedHeadCID
    ) public recordChainlinkFulfillment(_requestId) {
        emit RequestDisperseDataFulfilled(
            _requestId,
            _dispersalID,
            _lastUpdatedHeadCID
        );
        // string memory _projectID = jobRequestIDs[_requestId];
        dispersalRequests[_projectID].expectedTimeofDispersal =
            block.timestamp +
            1 minutes;
        dispersalRequests[_projectID].dispersalRequestID = _dispersalID;
        dispersalRequests[_projectID].lastUpdatedHeadCID = _lastUpdatedHeadCID;
    }

    /**
     * 
     * @param _projectID unique ID of project
     */
    function requestConfirmData(string memory _projectID) public onlyOwner {
        Chainlink.Request memory req = _buildOperatorRequest(
            CONFIRM_JOB_ID,
            this.fulfillConfirmData.selector
        );
        require(
            dispersalRequests[_projectID].expectedTimeofDispersal <
                block.timestamp,
            "please wait"
        );
        req._add("projectID", _projectID);
        req._add(
            "dispersalRequestID",
            dispersalRequests[_projectID].dispersalRequestID
        );
        _sendChainlinkRequestTo(OPERATOR_ADDRESS, req, ORACLE_PAYMENT);
    }

    /**
     * 
     * @param _requestId ID of Chainlink job request
     */
    function fulfillConfirmData(
        bytes32 _requestId,
        bool _isConfirmed,
        string memory _projectID
    ) public recordChainlinkFulfillment(_requestId) {
        // optionally call the verification function on fulfillment
        if (_isConfirmed) {
            IProjectStorageVerifier(projectVerifier).verifyProjectStorageProof(_projectID);
        }
        emit RequestConfirmDataFulfilled(
            _requestId,
            _isConfirmed,
            _projectID,
            projectVerifier
        );
    }


    // function requestRetrieveData(
    //     uint _date,
    //     bytes32 _projectID
    // ) public onlyOwner {
    //     Chainlink.Request memory req = _buildOperatorRequest(
    //         DATA_JOB_ID,
    //         this.fulfillRetrieveData.selector
    //     );
    //     req._addBytes("projectID", abi.encodePacked(_projectID));
    //     req._addUint("date", _date);
    //     _sendChainlinkRequestTo(OPERATOR_ADDRESS, req, ORACLE_PAYMENT);
    //     jobRequestIDs[req.id] = _projectID;
    // }


    // function fulfillRetrieveData(
    //     bytes32 _requestId,
    //     uint256 _agbData,
    //     uint256 _defData,
    //     uint256 _seqData,
    //     string calldata _agbUnit,
    //     string calldata _defUnit,
    //     string calldata _seqUnit
    // ) public recordChainlinkFulfillment(_requestId) {
    //     emit RequestRetrieveDataFulfilled(
    //         _requestId,
    //         _agbUnit,
    //         _defUnit,
    //         _seqUnit
    //     );
    //     carbonDataQueries[jobRequestIDs[_requestId]] = CarbonDataQuery({
    //         agb: _agbData,
    //         deforestation: _defData,
    //         sequestration: _seqData
    //     });
    // }


    function getChainlinkToken() public view returns (address) {
        return _chainlinkTokenAddress();
    }


    function withdrawLink() public onlyOwner {
        LinkTokenInterface link = LinkTokenInterface(_chainlinkTokenAddress());
        require(
            link.transfer(msg.sender, link.balanceOf(address(this))),
            "Unable to transfer"
        );
    }


    function cancelRequest(
        bytes32 _requestId,
        uint256 _payment,
        bytes4 _callbackFunctionId,
        uint256 _expiration
    ) public onlyOwner {
        _cancelChainlinkRequest(
            _requestId,
            _payment,
            _callbackFunctionId,
            _expiration
        );
    }

    // needed if JOB_ID is not hardcoded
    // function stringToBytes32(
    //     string memory source
    // ) private pure returns (bytes32 result) {
    //     bytes memory tempEmptyStringTest = bytes(source);
    //     if (tempEmptyStringTest.length == 0) {
    //         return 0x0;
    //     }

    //     assembly {
    //         // solhint-disable-line no-inline-assembly
    //         result := mload(add(source, 32))
    //     }
    // }
}

