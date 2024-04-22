// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Script.sol";
import "forge-std/console.sol";
import {EigenDARollupUtils, IEigenDAServiceManager, BN254, EigenDAHasher} from "../lib/eigenda/contracts/src/libraries/EigenDARollupUtils.sol";


contract BlobVerify is Script {
    function run() external {
        vm.startBroadcast();

        IEigenDAServiceManager.QuorumBlobParam[] memory quorumBlobParams = new IEigenDAServiceManager.QuorumBlobParam[](2);

        quorumBlobParams[0] = IEigenDAServiceManager.QuorumBlobParam(
            /*quorumNumber*/ 0,
            /*adversaryThresholdPercentage*/ 33,
            /*quorumThresholdPercentage*/ 55,
            /*chunkLength*/ 1);
        quorumBlobParams[1] = IEigenDAServiceManager.QuorumBlobParam(
            /*quorumNumber*/ 1,
            /*adversaryThresholdPercentage*/ 33,
            /*quorumThresholdPercentage*/ 55,
            /*chunkLength*/ 1);

        IEigenDAServiceManager.BlobHeader memory blobHeader = IEigenDAServiceManager.BlobHeader(
            BN254.G1Point(/*X*/13277593240034746755575358362670673584121304267561004413607076146471086711169,
                        /*Y*/13192003727366494670266473099047920856533648517910844148499933230800769300473),
            /*dataLength*/ 1,
            quorumBlobParams
        );

        address eigenDAServiceManager = 0xD4A7E1Bd8015057293f0D0A557088c286942e84b;
        
        uint256 blobRoot = 2862042700323737535500424407868240989973862023388377394631339889724415034243;
        IEigenDAServiceManager.BatchHeader memory batchHeader 
            = IEigenDAServiceManager.BatchHeader(
                /*bytes32 blobHeadersRoot*/ bytes32(blobRoot),
                /*bytes quorumNumbers*/ hex"0001",
                /*bytes quorumThresholdPercentages*/ hex"5650",
                /*uint32 referenceBlockNumber*/ 1326297
            );

        IEigenDAServiceManager.BatchMetadata memory batchMetadata
            = IEigenDAServiceManager.BatchMetadata(
                batchHeader,
                /*bytes32 signatoryRecordHash*/ 0x4a362962c7a164b25a6f4ec54ab7af016b13ba42a7782807d8a591578cd79da4,
                /*uint32 confirmationBlockNumber*/ 1326405
            );

        EigenDARollupUtils.BlobVerificationProof memory blobVerificationProof
            = EigenDARollupUtils.BlobVerificationProof({
                /*uint32 batchId*/ batchId: 9886,
                /*uint32 blobIndex*/ blobIndex: 244,
                batchMetadata: batchMetadata,
                /*bytes inclusionProof*/ inclusionProof: hex"635af3a774906c593ab765ea5f377bc8274ed336ab1c1557a9066bc1af661175ac564b8ccc43650c526ee51438c1a206583b7cd5948cccd4ebf49dd95d64fe94b9b5137b1b2b5757b9521f180f1abb5298503c838344479f20928bc5e88d6bf1d55a043e82bb2ae182f9792acfcca7230b0b078b9a027ca356f993d282b5a36f12c58b8394a2d5782ed698c83696fe09fae62cb32f18d1657f5eea0f8bc52f0087853c4cc707e5db62a40c738cf29c465eff8edc604a3d0ee315cf0435a39d2cbbff5cfdcba55a9c22ad8bf29391d372950d506a8e110c182aaf5323a9c4c1728abab16822150e70383a9d9a918fcc0ad29e343b9d27db09e967dec494f48738c030d3abc04ca526ad3ffa9a22a83e899545ff5e584fdc206d350e553ad47a4c",
                /*bytes quorumThresholdIndexes*/ quorumIndices: hex"0001"
    });

        EigenDARollupUtils.verifyBlob(blobHeader, IEigenDAServiceManager(eigenDAServiceManager), blobVerificationProof);

        vm.stopBroadcast();
    }
}