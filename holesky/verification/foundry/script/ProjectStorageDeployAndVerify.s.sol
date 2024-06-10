// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Script.sol";
import "forge-std/console.sol";
import "../src/ProjectStorageVerifier.sol";


contract ProjectStorageDeployAndVerify is Script {
    function run() external {   
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        address owner = vm.envAddress("WALLET_ADDRESS");
        vm.startBroadcast(deployerPrivateKey);

        ProjectStorageVerifier projectStorageVerifier = new ProjectStorageVerifier(owner);

        string memory projectName = "project-test";
        // PLACEHOLDER
        string memory lastUpdatedHeadCID = "";
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

        BlobVerifier.ModifiedBlobHeader memory blobHeader = BlobVerifier.ModifiedBlobHeader({
            commitment: BN254.G1Point(
                18171297588696763929626849511322678416393695719385988237656895665615483177907,
                4301955005949362388327180169304248503021139659975673245499737657633538138245
            ),
            dataLength: 13,
            batchHeaderHash: hex"ca716ebb16aae9326da20a7affbaef32523b6c5f05ff23bfbcd9d50e5120f38f",
            quorumNumbers: quorumNumbers,
            adversaryThresholdPercentages: adversaryThresholdPercentages,
            confirmationThresholdPercentages: confirmationThresholdPercentages,
            chunkLengths: chunkLengths
        });

        EigenDARollupUtils.BlobVerificationProof memory blobVerificationProof = EigenDARollupUtils.BlobVerificationProof({
            batchId: 18626,
            blobIndex: 799,
            batchMetadata: IEigenDAServiceManager.BatchMetadata({
                batchHeader: IEigenDAServiceManager.BatchHeader({
                    blobHeadersRoot: hex"15903f29064a1b20b965b66f932067bf476782fab466d2bad580a0600f8881e3",
                    quorumNumbers: hex"0001",
                    signedStakeForQuorums: hex"5e5f",
                    referenceBlockNumber: 1709546
                }),
                signatoryRecordHash: hex"b731817edaaa402bf57d9dc17d7535bc3a0d0c7d36e72b8b368050baa6251ea6",
                confirmationBlockNumber: 1709670
            }),
            inclusionProof: hex"154044d7f4e1c56a0a2d00f1440cf73f06d9a73676578127eb8d2b7a767160443f5826095621dd80f61b4a4ff414eca6288ed9699661ddacf7c3b9ddfaaef34dd8a3e2e2572f03c46dcd963660982fef15186c7109a589d04a151e25b5c02f0fdfada51882930c71bd3fdb89cceb8334b089c765d40b0199ffc601c8d7dc8b2ba78d91a043b2c5a0f58c02169f6e9a62b1f59e0eaeeeb1794305b422b4eee984571b272cfff3f877f7d78a2e3c38aa7264250572555a1abac7af11b45286ba04acbcc250a3960f575fce50391af36b95e913f12981a578e3b537bf5511a70cc41cd42639f03e16ef75baf170bbd37817aa032732064314432ce2dd835c26fc5dc67b622f6916d1de8ac5a299e6c3964fc1e18c89cc3c900070e7e9c48d20861c67474f343b55ea085830fac71b884f4c57f9e04d2bc63559d009dd1aef27a9cf51badedd31f91c56c1ace248c94a2902914841dabc19841c8a1a9d0888a6df3c",
            quorumIndices: hex"0001"
        });

        projectStorageVerifier.uploadProjectStorageProof(
            projectName, 
            lastUpdatedHeadCID, 
            blobHeader, 
            blobVerificationProof
        );
        projectStorageVerifier.verifyProjectStorageProof(projectName);
        projectStorageVerifier.readProjectStorageProof(projectName);

        vm.stopBroadcast();
    }

}
