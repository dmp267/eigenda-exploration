// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {EigenDARollupUtils, BN254} from "../../lib/eigenda/contracts/src/libraries/EigenDARollupUtils.sol";


interface IBlobVerifier {

    // STRUCTS
    struct ModifiedBlobHeader {
        BN254.G1Point commitment;
        uint32 dataLength;
        bytes32 batchHeaderHash;
        uint8[] quorumNumbers;
        uint8[] adversaryThresholdPercentages;
        uint8[] confirmationThresholdPercentages; 
        uint32[] chunkLengths;
    }

    struct StorageDetail {
        uint256 lastUpdatedTimestamp;
        ModifiedBlobHeader blobHeader;
        EigenDARollupUtils.BlobVerificationProof blobVerificationProof;
    }

    // FUNCTIONS
    function grantSetterRole(address _setter) external;


    function readStorageDetail(string calldata id) external 
        returns (StorageDetail memory);


    function setStorageDetail(
        ModifiedBlobHeader calldata _blobHeader,
        EigenDARollupUtils.BlobVerificationProof calldata _blobVerificationProof,
        string calldata id
    ) external;


    function verifyAttestation(
        string memory id
    ) external;
}