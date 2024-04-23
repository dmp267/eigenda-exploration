// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {EigenDARollupUtils, IEigenDAServiceManager, BN254} from "../lib/eigenda/contracts/src/libraries/EigenDARollupUtils.sol";
import "../lib/openzeppelin-contracts/contracts/access/Ownable.sol";


contract BlobVerifier is Ownable {

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


    struct ModifiedBlobHeader {
        BN254.G1Point commitment;
        uint32 dataLength;
        uint8[] quorumNumbers;
        uint8[] adversaryThresholdPercentages;
        uint8[] confirmationThresholdPercentages; 
        uint32[] chunkLengths;
    }
    
    // holesky
    address serviceManagerAddress = 0xD4A7E1Bd8015057293f0D0A557088c286942e84b;

    struct StorageDetail {
        ModifiedBlobHeader blobHeader;
        EigenDARollupUtils.BlobVerificationProof blobVerificationProof;
    }

    StorageDetail[] public storageDetails;
    mapping (string => uint) public storageDetailsIndex; // index + 1


    constructor(address owner) Ownable(owner) {}


    function initializeStorageDetail(string memory cid) private {
        if (storageDetailsIndex[cid] == 0) {
            uint index = storageDetails.length;
            storageDetailsIndex[cid] = index + 1;

            storageDetails.push(StorageDetail({
                blobHeader: ModifiedBlobHeader({
                    commitment: BN254.G1Point(0, 0),
                    dataLength: 0,
                    quorumNumbers: new uint8[](0),
                    adversaryThresholdPercentages: new uint8[](0),
                    confirmationThresholdPercentages: new uint8[](0),
                    chunkLengths: new uint32[](0)
                }),
                blobVerificationProof: EigenDARollupUtils.BlobVerificationProof({
                    batchId: 0,
                    blobIndex: 0,
                    batchMetadata: IEigenDAServiceManager.BatchMetadata({
                        batchHeader: IEigenDAServiceManager.BatchHeader({
                            blobHeadersRoot: bytes32(0),
                            quorumNumbers: new bytes(0),
                            signedStakeForQuorums: new bytes(0),
                            referenceBlockNumber: 0
                        }),
                        signatoryRecordHash: bytes32(0),
                        confirmationBlockNumber: 0
                    }),
                    inclusionProof: new bytes(0),
                    quorumIndices: new bytes(0)
                })
            }));
        } 
    }


    function setBlobHeader(
        uint32 dataLength,
        uint256 x,
        uint256 y,
        uint8[] calldata quorumNumbers,
        uint8[] calldata adversaryThresholdPercentages,
        uint8[] calldata confirmationThresholdPercentages,
        uint32[] calldata chunkLengths,
        string memory cid // calldata limit
    ) external onlyOwner {
        uint index = storageDetailsIndex[cid];
        if (index == 0) {
            initializeStorageDetail(cid);
        }

        index = storageDetailsIndex[cid] - 1;
        storageDetails[index].blobHeader = ModifiedBlobHeader({
            commitment: BN254.G1Point(x, y),
            dataLength: dataLength,
            quorumNumbers: quorumNumbers,
            adversaryThresholdPercentages: adversaryThresholdPercentages,
            confirmationThresholdPercentages: confirmationThresholdPercentages,
            chunkLengths: chunkLengths
        });
    }


    function setBatchMetadata(
        bytes32 signatoryRecordHash,
        uint32 confirmationBlockNumber,
        bytes32 blobHeadersRoot,
        uint32 referenceBlockNumber,
        bytes calldata quorumNumbers,
        bytes calldata signedStakeForQuorums,
        string calldata cid
    ) external onlyOwner {
        uint index = storageDetailsIndex[cid];
        if (index == 0) {
            initializeStorageDetail(cid);
        } 

        index = storageDetailsIndex[cid] - 1;
        storageDetails[index].blobVerificationProof.batchMetadata = IEigenDAServiceManager.BatchMetadata({
            batchHeader: IEigenDAServiceManager.BatchHeader({
                blobHeadersRoot: blobHeadersRoot,
                quorumNumbers: quorumNumbers,
                signedStakeForQuorums: signedStakeForQuorums,
                referenceBlockNumber: referenceBlockNumber
            }),
            signatoryRecordHash: signatoryRecordHash,
            confirmationBlockNumber: confirmationBlockNumber
        });
    }


    function setBlobVerificationProof(
        uint32 batchId,
        uint32 blobIndex,
        bytes calldata inclusionProof,
        bytes calldata quorumIndices,
        string calldata cid
    ) external onlyOwner {
        uint index = storageDetailsIndex[cid];
        if (index == 0) {
            initializeStorageDetail(cid);
        } 

        index = storageDetailsIndex[cid] - 1;
        storageDetails[index].blobVerificationProof = EigenDARollupUtils.BlobVerificationProof({
            batchId: batchId,
            blobIndex: blobIndex,
            batchMetadata: storageDetails[index].blobVerificationProof.batchMetadata,
            inclusionProof: inclusionProof,
            quorumIndices: quorumIndices
        });
    }
        

    function verifyAttestation(
        string memory cid
    ) 
        public 
        view
    {
        uint index = storageDetailsIndex[cid];
        require(index > 0, "BlobVerifier: invalid cid");
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


