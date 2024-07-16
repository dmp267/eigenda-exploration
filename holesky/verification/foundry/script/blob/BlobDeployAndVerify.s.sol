// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Script.sol";
import "forge-std/console.sol";
import "../../src/BlobVerifier.sol";
import "../../src/IBlobVerifier.sol";


contract BlobDeployAndVerify is Script {

    string constant CID = "QmSoASxb8aNVGk3pNWpZvXEZTQKxjGeu9bvpYHuo5bP1VJ";

    function run() external {   
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        address owner = vm.envAddress("WALLET_ADDRESS");
        vm.startBroadcast(deployerPrivateKey);

        BlobVerifier blobVerifier = new BlobVerifier(owner);

        uint8[] memory quorumNumbers = new uint8[](2);
        quorumNumbers[0] = 0;
        quorumNumbers[1] = 1;
        uint8[] memory adversaryThresholdPercentages = new uint8[](2);
        adversaryThresholdPercentages[0] = 33;
        adversaryThresholdPercentages[1] = 33;
        uint8[] memory confirmationThresholdPercentages = new uint8[](2);
        confirmationThresholdPercentages[0] = 55;
        confirmationThresholdPercentages[1] = 55;
        uint32[] memory chunkLengths = new uint32[](2);
        chunkLengths[0] = 1;
        chunkLengths[1] = 1;

        BlobVerifier.ModifiedBlobHeader memory blobHeader = IBlobVerifier.ModifiedBlobHeader({
            commitment: BN254.G1Point(
                17709391318787797331642701840504388161158975750185246830022501631687012546893,
                5511369121926248436136882980770562785844228494401429094386919117721689758478
            ),
            dataLength: 1,
            batchHeaderHash: hex"829b163ab6bafa5474f6e6a99fcde9ee2e5978e9c75a0670700e92748a2a3f95",
            quorumNumbers: quorumNumbers,
            adversaryThresholdPercentages: adversaryThresholdPercentages,
            confirmationThresholdPercentages: confirmationThresholdPercentages,
            chunkLengths: chunkLengths
        });

        EigenDARollupUtils.BlobVerificationProof memory blobVerificationProof = EigenDARollupUtils.BlobVerificationProof({
            batchId: 11550,
            blobIndex: 805,
            batchMetadata: IEigenDAServiceManager.BatchMetadata({
                batchHeader: IEigenDAServiceManager.BatchHeader({
                    blobHeadersRoot: hex"df69a32cd0589de5096ce85b627c40c390551a03bc3e1415213686422fa18bbf",
                    quorumNumbers: hex"0001",
                    signedStakeForQuorums: hex"6362",
                    referenceBlockNumber: 1398667
                }),
                signatoryRecordHash: hex"dd5ceff68423495260173cc698a7cb12eead967f43239e58fec53af966863154",
                confirmationBlockNumber: 1398800
            }),
            inclusionProof: hex"ddfb9c5534618e284d50cd9aaa69b698f57e7c975a62da7cbcbba93ae53c175594a7a9aad947143173bfb7f3c143fdac4e976243dadaa0f8d452a3d92841b3ad007f1652540091ebd4fe75ea367ea3cc2111e9e7b578494296995a41d730083188e3df71366089cbf1757acd13460d14ddee6a7c0ab0f2d15cddecfb1272bbc3c94e723a5cccd1be0a233730a9add4c683786957761454bf4f317253be349ae7c32565a56aecf6e9bbc6cfb56c461f6063273cc50ddc7b7ec9d9704f13284a356a0b0781391e39012c7ef74bd5b98bcd40b1ca1c99404c51c89fdb4401f090bb0a89204793e3c7279de021163f73cbd088ecd14e970220ca6644324961ddf22b50b137ac7a6325934bf8504476bfd88ac1f92850400fdbb0b5a0de8be74b3306108246455a16b90e0032bb76081177992f9ae0736bd08da49cfb1eac55812de3873aa7a12116b7c3d880680b86369459775e3e250f24fd4c375d163f59dcfaaa",
            quorumIndices: hex"0001"
        });

        blobVerifier.setStorageDetail(blobHeader, blobVerificationProof, CID);
        blobVerifier.verifyAttestation(CID);

        vm.stopBroadcast();
    }
}