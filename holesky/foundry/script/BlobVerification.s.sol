// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Script.sol";
import {EigenDARollupUtils, IEigenDAServiceManager, BN254} from "../lib/eigenda/contracts/src/libraries/EigenDARollupUtils.sol";


contract BlobVerifierDeployer is Script {
    function run() external {
        vm.startBroadcast();

        IEigenDAServiceManager.QuorumBlobParam[] memory quorumBlobParams = new IEigenDAServiceManager.QuorumBlobParam[](2);

        quorumBlobParams[0] = IEigenDAServiceManager.QuorumBlobParam(
            /*quorumNumber*/0,
            /*adversaryThresholdPercentage*/33,
            /*quorumThresholdPercentage*/50,
            /*chunkLength*/1);
        quorumBlobParams[1] = IEigenDAServiceManager.QuorumBlobParam(
            /*quorumNumber*/1,
            /*adversaryThresholdPercentage*/33,
            /*quorumThresholdPercentage*/50,
            /*chunkLength*/1);

        IEigenDAServiceManager.BlobHeader memory blobHeader = IEigenDAServiceManager.BlobHeader(
            BN254.G1Point(/*X*/13277593240034746755575358362670673584121304267561004413607076146471086711169,
                        /*Y*/13192003727366494670266473099047920856533648517910844148499933230800769300473),
            /*dataLength*/ 1,
            quorumBlobParams
        );

        address eigenDAServiceManager = 0xD4A7E1Bd8015057293f0D0A557088c286942e84b;
        //0x1eEa1C6b573f192F33BE6AA56dC9080314a89491;
        
        uint256 blobRoot = 2862042700323737535500424407868240989973862023388377394631339889724415034243;
        IEigenDAServiceManager.BatchHeader memory batchHeader 
            = IEigenDAServiceManager.BatchHeader(
                /*bytes32 blobHeadersRoot*/ bytes32(blobRoot),
                /*bytes quorumNumbers*/ hex"01",
                /*bytes quorumThresholdPercentages*/ hex"84", // pad base64 to mult of 4 chars, decode b64, then convert to hex?
                /*uint32 referenceBlockNumber*/ 1326297
            );

        IEigenDAServiceManager.BatchMetadata memory batchMetadata
            = IEigenDAServiceManager.BatchMetadata(
                batchHeader,
                /*bytes32 signatoryRecordHash*/ 0x4a362962c7a164b25a6f4ec54ab7af016b13ba42a7782807d8a591578cd79da4,
                /*uint32 confirmationBlockNumber*/1326405
            );

        EigenDARollupUtils.BlobVerificationProof memory blobVerificationProof
            = EigenDARollupUtils.BlobVerificationProof(
                /*uint32 batchId*/ 9886,
                /*uint8 blobIndex*/ 244,
                batchMetadata,
                /*bytes inclusionProof*/ hex"1452315584500823761586621845932611725842094991274866349044949851450750386146530127330210334797718151731747407751125751212242085850799052238598220617840739481048370412769600499608177734868137111322719780076927597816035738614260536250572835583772274439678653949777227891699407600958924186434265981332475362008001983255972651990816135569661608750393868027149158171311917928070087099119457435643979717035631122870625624952092209332187345807590381358068914864993598361020469320475960603697038513630575295985520192476274382673869078055226606478350551249659625694056927898383677868269482711369566335010483140382444651150923877004442372445523679942122628627893224415414304825887444113042000183385422412",
                /*bytes quorumThresholdIndexes*/ hex"01"
            );

        EigenDARollupUtils.verifyBlob(blobHeader, IEigenDAServiceManager(eigenDAServiceManager), blobVerificationProof);

        vm.stopBroadcast();
    }
}