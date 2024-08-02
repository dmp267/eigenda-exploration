// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {IBlobVerifier, EigenDARollupUtils} from "./IBlobVerifier.sol";


interface IProjectStorageVerifier is IBlobVerifier {

    // STRUCTS
    // struct ProjectStore {
    //     bool exists;
    //     string lastUpdatedHeadCID;
    //     // coords?
    // }


    struct FullStore {
        bool exists;
        IBlobVerifier.StorageDetail storageDetail;
    }


    // FUNCTIONS
    function uploadProjectStorageProof(
        string calldata projectID,
        // string calldata lastUpdatedHeadCID,
        IBlobVerifier.ModifiedBlobHeader calldata _blobHeader,
        EigenDARollupUtils.BlobVerificationProof calldata _blobVerificationProof
    ) external;


    function verifyProjectStorageProof(string memory projectID) external;


    function readProjectStorageProof(string calldata projectID) 
        external returns (FullStore memory);


    // function updateProjectStorageId(string calldata projectID, string calldata newProjectID) external;
}