// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {IBlobVerifier, EigenDARollupUtils} from "./IBlobVerifier.sol";


interface IProjectStorageVerifier {

    // STRUCTS
    struct ProjectStore {
        bool exists;
        string lastUpdatedHeadCID;
        // coords?
    }


    struct FullStore {
        ProjectStore projectStore;
        IBlobVerifier.StorageDetail storageDetail;
    }


    // FUNCTIONS
    function uploadProjectStorageProof(
        string calldata projectID,
        string calldata lastUpdatedHeadCID,
        IBlobVerifier.ModifiedBlobHeader calldata _blobHeader,
        EigenDARollupUtils.BlobVerificationProof calldata _blobVerificationProof
    ) external;


    function verifyProjectStorageProof(string calldata projectID) 
        external;


    function readProjectStorageProof(string calldata projectID) 
        external returns (FullStore memory);
}