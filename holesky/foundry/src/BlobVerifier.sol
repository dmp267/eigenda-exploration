// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;


import {IEigenDAServiceManager, BlobVerificationProof, verifyBlob} from "../lib/eigenda/contracts/src/libraries/EigenDARollupUtils.sol";


contract BlobVerifier {

    // struct G1Point {
    //     uint256 X;
    //     uint256 Y;
    // }

    // struct QuorumBlobParam {
    //     uint8 quorumNumber;
    //     uint8 adversaryThresholdPercentage;
    //     uint8 confirmationThresholdPercentage; 
    //     uint32 chunkLength; // the length of the chunks in the quorum
    // }

    // struct BlobHeader {
    //     BN254.G1Point commitment; // the kzg commitment to the blob
    //     uint32 dataLength; // the length of the blob in coefficients of the polynomial
    //     QuorumBlobParam[] quorumBlobParams; // the quorumBlobParams for each quorum
    // }

    // struct BatchHeader {
    //     bytes32 blobHeadersRoot;
    //     bytes quorumNumbers; // each byte is a different quorum number
    //     bytes signedStakeForQuorums; // every bytes is an amount less than 100 specifying the percentage of stake 
    //                                  // that has signed in the corresponding quorum in `quorumNumbers` 
    //     uint32 referenceBlockNumber;
    // }

    // struct BatchMetadata {
    //     BatchHeader batchHeader; // the header of the data store
    //     bytes32 signatoryRecordHash; // the hash of the signatory record
    //     uint32 confirmationBlockNumber; // the block number at which the batch was confirmed
    // }

    // struct BlobVerificationProof {
    //     uint32 batchId;
    //     uint32 blobIndex;
    //     IEigenDAServiceManager.BatchMetadata batchMetadata;
    //     bytes inclusionProof;
    //     bytes quorumIndices;
    // }

    function verifyProofOfBlobStorage(
        IEigenDAServiceManager.BlobHeader memory _blobHeader, 
        IEigenDAServiceManager _eigenDAServiceManager,
        BlobVerificationProof memory _blobVerificationProof
    ) 
        public 
        pure 
        returns (bool) 
    {
        return verifyBlob(
            _blobHeader, 
            _eigenDAServiceManager, 
            _blobVerificationProof
        );
    }
}


