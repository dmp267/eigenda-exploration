// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {EigenDARollupUtils, IEigenDAServiceManager, BN254} from "../lib/eigenda/contracts/src/libraries/EigenDARollupUtils.sol";


contract BlobVerifier {

    // struct G1Point {
    //     uint256 X;
    //     uint256 Y;
    // }

    // struct IEigenDAServiceManager.QuorumBlobParam {
    //     uint8 quorumNumber;
    //     uint8 adversaryThresholdPercentage;
    //     uint8 confirmationThresholdPercentage; 
    //     uint32 chunkLength; // the length of the chunks in the quorum
    // }

    // struct IEigenDAServiceManager.BlobHeader {
    //     BN254.G1Point commitment; // the kzg commitment to the blob
    //     uint32 dataLength; // the length of the blob in coefficients of the polynomial
    //     QuorumBlobParam[] quorumBlobParams; // the quorumBlobParams for each quorum
    // }

    // struct IEigenDAServiceManager.BatchHeader {
    //     bytes32 blobHeadersRoot;
    //     bytes quorumNumbers; // each byte is a different quorum number
    //     bytes signedStakeForQuorums; // every bytes is an amount less than 100 specifying the percentage of stake 
    //                                  // that has signed in the corresponding quorum in `quorumNumbers` 
    //     uint32 referenceBlockNumber;
    // }

    // struct IEigenDAServiceManager.BatchMetadata {
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

    // holesky
    address serviceManagerAddress = 0xD4A7E1Bd8015057293f0D0A557088c286942e84b;
    IEigenDAServiceManager.BlobHeader blobHeader;
    IEigenDAServiceManager.BatchMetadata batchMetadata;


    function setBlobHeader(
        uint32 dataLength,
        uint256 x,
        uint256 y,
        uint8[] memory quorumNumbers,
        uint8[] memory adversaryThresholdPercentages,
        uint8[] memory confirmationThresholdPercentages,
        uint32[] memory chunkLengths
    )
        external
    {
        BN254.G1Point memory commitment = BN254.G1Point(x, y);
        IEigenDAServiceManager.QuorumBlobParam[] memory quorumBlobParams = new IEigenDAServiceManager.QuorumBlobParam[](quorumNumbers.length);

        for (uint i = 0; i < quorumNumbers.length; i++) {
            quorumBlobParams[i] = IEigenDAServiceManager.QuorumBlobParam({
                quorumNumber: quorumNumbers[i],
                adversaryThresholdPercentage: adversaryThresholdPercentages[i],
                confirmationThresholdPercentage: confirmationThresholdPercentages[i],
                chunkLength: chunkLengths[i]
            });
        }
        blobHeader = IEigenDAServiceManager.BlobHeader({
            commitment: commitment,
            dataLength: dataLength,
            quorumBlobParams: quorumBlobParams
        });
    }


    function setBatchMetadata(
        bytes32 signatoryRecordHash,
        uint32 confirmationBlockNumber,
        bytes32 blobHeadersRoot,
        uint32 referenceBlockNumber,
        bytes memory quorumNumbers,
        bytes memory signedStakeForQuorums
    )
        external
    {
        IEigenDAServiceManager.BatchHeader memory batchHeader = IEigenDAServiceManager.BatchHeader({
            blobHeadersRoot: blobHeadersRoot,
            quorumNumbers: quorumNumbers,
            signedStakeForQuorums: signedStakeForQuorums,
            referenceBlockNumber: referenceBlockNumber
        });


        batchMetadata = IEigenDAServiceManager.BatchMetadata({
            batchHeader: batchHeader,
            signatoryRecordHash: signatoryRecordHash,
            confirmationBlockNumber: confirmationBlockNumber
        });
    }
        

    function verifyAttestation(
        uint32 batchId,
        uint32 blobIndex,
        bytes memory inclusionProof,
        bytes memory quorumIndices
    ) 
        public 
        view
    {
        IEigenDAServiceManager.BlobHeader memory _blobHeader = blobHeader;
        IEigenDAServiceManager _eigenDAServiceManager = IEigenDAServiceManager(serviceManagerAddress);
        EigenDARollupUtils.BlobVerificationProof memory _blobVerificationProof = EigenDARollupUtils.BlobVerificationProof({
            batchId: batchId,
            blobIndex: blobIndex,
            batchMetadata: batchMetadata,
            inclusionProof: inclusionProof,
            quorumIndices: quorumIndices
        });

        EigenDARollupUtils.verifyBlob(_blobHeader, _eigenDAServiceManager, _blobVerificationProof);
    }
}


