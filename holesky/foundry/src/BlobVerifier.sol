// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {EigenDARollupUtils, IEigenDAServiceManager, BN254} from "../lib/eigenda/contracts/src/libraries/EigenDARollupUtils.sol";
import "../lib/openzeppelin-contracts/contracts/access/Ownable.sol";


contract BlobVerifier is Ownable {

    struct ModifiedBlobHeader {
        BN254.G1Point commitment;
        uint32 dataLength;
        bytes32 batchHeaderHash;
        uint8[] quorumNumbers;
        uint8[] adversaryThresholdPercentages;
        uint8[] confirmationThresholdPercentages; 
        uint32[] chunkLengths;
    }
    
    // HOLESKY
    address constant serviceManagerAddress = 0xD4A7E1Bd8015057293f0D0A557088c286942e84b;

    struct StorageDetail {
        ModifiedBlobHeader blobHeader;
        EigenDARollupUtils.BlobVerificationProof blobVerificationProof;
    }

    StorageDetail[] internal storageDetails;
    mapping (string => uint) internal storageDetailsIndex; // always stores index + 1 to differentiate from default value 0


    constructor(address owner) Ownable(owner) {}

    function readStorageDetail(string calldata id) 
        public 
        view 
        returns (StorageDetail memory) 
    {
        uint index = storageDetailsIndex[id];
        require(index > 0, "BlobVerifier: invalid id");
        return storageDetails[index - 1];
    }


    function setStorageDetail(
        ModifiedBlobHeader calldata _blobHeader,
        EigenDARollupUtils.BlobVerificationProof calldata _blobVerificationProof,
        string calldata id
    ) public onlyOwner {
        uint index = storageDetailsIndex[id];
        if (index == 0) {
            index = storageDetails.length + 1;
            storageDetailsIndex[id] = index;
            storageDetails.push(StorageDetail({
                blobHeader: _blobHeader,
                blobVerificationProof: _blobVerificationProof
            }));
        } 
        storageDetails[index - 1].blobHeader = _blobHeader;
        storageDetails[index - 1].blobVerificationProof = _blobVerificationProof;
    }
        

    function verifyAttestation(
        string memory id
    ) 
        public 
        view
    {
        uint index = storageDetailsIndex[id];
        require(index > 0, "BlobVerifier: invalid id");
        StorageDetail memory _storageDetails = storageDetails[index - 1];
        IEigenDAServiceManager _eigenDAServiceManager = IEigenDAServiceManager(serviceManagerAddress);

        IEigenDAServiceManager.QuorumBlobParam[] memory _quorumBlobParams = new IEigenDAServiceManager.QuorumBlobParam[](_storageDetails.blobHeader.quorumNumbers.length);

        for (uint i = 0; i < _storageDetails.blobHeader.quorumNumbers.length; i++) {
            _quorumBlobParams[i] = IEigenDAServiceManager.QuorumBlobParam({
                quorumNumber: _storageDetails.blobHeader.quorumNumbers[i],
                adversaryThresholdPercentage: _storageDetails.blobHeader.adversaryThresholdPercentages[i],
                confirmationThresholdPercentage: _storageDetails.blobHeader.confirmationThresholdPercentages[i],
                chunkLength: _storageDetails.blobHeader.chunkLengths[i]
            });
        }

        IEigenDAServiceManager.BlobHeader memory _blobHeader = IEigenDAServiceManager.BlobHeader({
            commitment: _storageDetails.blobHeader.commitment,
            dataLength: _storageDetails.blobHeader.dataLength,
            quorumBlobParams: _quorumBlobParams
        });

        EigenDARollupUtils.verifyBlob(_blobHeader, _eigenDAServiceManager, _storageDetails.blobVerificationProof);
    }
}


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
