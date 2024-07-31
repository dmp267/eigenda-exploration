// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {Chainlink, ChainlinkClient} from "../../lib/chainlink/contracts/src/v0.8/ChainlinkClient.sol";
import {ConfirmedOwner} from "../../lib/chainlink/contracts/src/v0.8/shared/access/ConfirmedOwner.sol";
import {LinkTokenInterface} from "../../lib/chainlink/contracts/src/v0.8/shared/interfaces/LinkTokenInterface.sol";
import {Strings} from "../../lib/openzeppelin-contracts/contracts/utils/Strings.sol";

import "../interfaces/ICarbonMonitoringVerifier.sol";
import "../interfaces/IProjectStorageVerifier.sol";


// import "forge-std/console.sol";

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
    // mapping(bytes32 => CarbonDataQuery) public carbonDataQueries;
    // 0: not initialized, 1: dispersal requested, 2: data confirmed, 3: data expired
    mapping(address => UserDetail) public userDetails;
    mapping(string => uint) public projectIndex; // projectID => index (+1)
    
    mapping(bytes32 => JobRequest) private jobRequests;


    constructor() ConfirmedOwner(msg.sender) {
        _setChainlinkToken(LINK_ADDRESS);
    }

    /**
     * 
     * @param _projectVerifier address of ProjectStorageVerifier contract
     */
    function setProjectVerifier(address _projectVerifier) external onlyOwner {
        projectVerifier = _projectVerifier;
    }


    function whitelistUser(address _userID) external onlyOwner {
        require(!userDetails[_userID].whitelisted, "user already whitelisted");
        userDetails[_userID].whitelisted = true;
    }


    function buildProjectID(
        address _user, 
        string memory _projectName
    ) private pure returns (string memory) {
        return string(abi.encodePacked(Strings.toHexString(uint256(uint160(_user)), 20), ":", _projectName));
    }


    function updateProjectState(
        address _user, 
        string memory _projectName
    ) external {
        string memory projectID = buildProjectID(_user, _projectName);
        uint index = projectIndex[projectID];
        require(index > 0, "project not found");
        UserProject memory project = userDetails[_user].userProjects[index - 1];
        if (project.expectedTimeofExpiry < block.timestamp) {
            userDetails[_user].userProjects[index - 1].projectState = 3;
            if (project.isSubscribed) {
                uint start = project.start;
                uint end = project.end;
                requestDisperseData(
                    true,
                    start,
                    end,
                    _projectName,
                    project.cid
                );
            }
        } else {
            if (project.expectedTimeofDispersal < block.timestamp && project.projectState == 1) {
                requestConfirmData(_user, _projectName);
            }
        }
    }
    
    /**
     * 
     * @param _isSubscription boolean indicating if user is subscribed to project
     * @param _start timestamp in 's' of start of desired range
     * @param _end timestamp in 's' of end of desired range
     * @param _projectName user-defined name of project
     * @param _cid CID of uploaded KML file on IPFS
     */
    function requestDisperseData(
        bool _isSubscription,
        uint _start,
        uint _end,
        string memory _projectName,
        string memory _cid
    ) public {
        require(
            userDetails[msg.sender].whitelisted,
            "user not whitelisted"
        );
        Chainlink.Request memory req = _buildOperatorRequest(
            DISPERSAL_JOB_ID,
            this.fulfillDisperseData.selector
        );
        string memory projectID = buildProjectID(msg.sender, _projectName);
        // string memory projectID = string(abi.encodePacked(Strings.toHexString(uint256(uint160(msg.sender)), 20), ":", _projectName));
        req._add("projectID", projectID);
        req._add("cid", _cid);
        req._addUint("start", _start);
        req._addUint("end", _end);
        bytes32 reqID = _sendChainlinkRequestTo(OPERATOR_ADDRESS, req, ORACLE_PAYMENT);
        jobRequests[reqID] = JobRequest({
            user: msg.sender,
            projectID: projectID
        });

        uint index = projectIndex[projectID];
        UserProject[] storage userProjects = userDetails[msg.sender].userProjects;
        if (index == 0) {
            userProjects.push(
                UserProject({
                    isSubscribed: _isSubscription,
                    projectState: 1,
                    start: _start,
                    end: _end,
                    expectedTimeofDispersal: block.timestamp + 2 minutes,
                    expectedTimeofExpiry: block.timestamp + 10 days,
                    cid: _cid,
                    dispersalRequestID: "",
                    lastUpdatedHeadCID: ""
                })
            );
            index = userProjects.length;
            projectIndex[projectID] = index;
        }
        userProjects[index - 1].projectState = 1;
        userProjects[index - 1].cid = _cid;
    }

    /**
     * 
     * @param _requestId ID for Chainlink job request
     * @param _dispersalID ID for EigenDA dispersal request
     * @param _lastUpdatedHeadCID most recent IPFS head CID for associated datasets
     */
    function fulfillDisperseData(
        bytes32 _requestId,
        string memory _dispersalID,
        string memory _lastUpdatedHeadCID
    ) public recordChainlinkFulfillment(_requestId) { 
        emit RequestDisperseDataFulfilled(
            _requestId,
            _dispersalID,
            _lastUpdatedHeadCID
        );
        address user = jobRequests[_requestId].user;
        string memory projectID = jobRequests[_requestId].projectID;
        uint index = projectIndex[projectID];
        require(index > 0, "project not found");

        UserProject storage project = userDetails[user].userProjects[index - 1];
        project.expectedTimeofDispersal = block.timestamp + 10 minutes;
        project.dispersalRequestID = _dispersalID;
        project.lastUpdatedHeadCID = _lastUpdatedHeadCID;
        delete jobRequests[_requestId];
    }

    /**
     * 
     * @param _user address of user
     * @param _projectName user-defined name of project
     */
    function requestConfirmData(address _user, string memory _projectName) public {
        Chainlink.Request memory req = _buildOperatorRequest(
            CONFIRM_JOB_ID,
            this.fulfillConfirmData.selector
        );
        require(
            userDetails[msg.sender].whitelisted && userDetails[_user].whitelisted,
            "user(s) not whitelisted"
        );
        string memory projectID = buildProjectID(_user, _projectName);
        // string memory projectID = string(abi.encodePacked(Strings.toHexString(uint256(uint160(_user)), 20), ":", _projectName));
        uint index = projectIndex[projectID];
        require(index > 0, "project not found");
        require(
            userDetails[_user].userProjects[index - 1].expectedTimeofDispersal < block.timestamp,
            "please wait"
        );
        req._add("projectID", projectID);
        req._add(
            "dispersalRequestID",
            userDetails[_user].userProjects[index - 1].dispersalRequestID
        );
        bytes32 reqID = _sendChainlinkRequestTo(OPERATOR_ADDRESS, req, ORACLE_PAYMENT);
        jobRequests[reqID] = JobRequest({
            user: _user,
            projectID: projectID
        });
    }
    //  * @param _user address of user cast to uint256
    //  * @param _projectID unique ID of project
    /**
     * 
     * @param _requestId ID of Chainlink job request
     * @param _isConfirmed boolean indicating if data is confirmed
     */
    function fulfillConfirmData(
        bytes32 _requestId,
        bool _isConfirmed
    ) public recordChainlinkFulfillment(_requestId) {
        address user = jobRequests[_requestId].user;
        string memory _projectID = jobRequests[_requestId].projectID;
        uint index = projectIndex[_projectID];
        if (_isConfirmed) {
            IProjectStorageVerifier(projectVerifier).verifyProjectStorageProof(_projectID);
            userDetails[user].userProjects[index - 1].projectState = 2;
            userDetails[user].userProjects[index - 1].expectedTimeofExpiry = block.timestamp + 10 days;
        }
        emit RequestConfirmDataFulfilled(
            _requestId,
            _isConfirmed,
            _projectID,
            projectVerifier
        );
        delete jobRequests[_requestId];
    }


    // function requestRetrieveData(
    //     uint _date,
    //     string memory _projectID
    // ) public onlyOwner {
    //     Chainlink.Request memory req = _buildOperatorRequest(
    //         DATA_JOB_ID,
    //         this.fulfillRetrieveData.selector
    //     );
    //     req._add("projectID", _projectID);
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

