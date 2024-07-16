// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../contracts/BlobVerifier.sol";
import "../interfaces/IProjectStorageVerifier.sol";

// CURRENT DEPLOYED ADDRESS: 0x8032b4DBa3779B6836B4C69203bB1d3b4f92908B
contract ProjectStorageVerifier is IProjectStorageVerifier, BlobVerifier {

    // return type for readProjectStorageDetails
    // struct FullStore {
    //     ProjectStore projectStore;
    //     StorageDetail storageDetail;
    // }

    mapping(string => bool) public projects;


    constructor(address owner) BlobVerifier(owner) {}


    function uploadProjectStorageProof(
        string calldata projectID,
        // string calldata lastUpdatedHeadCID,
        ModifiedBlobHeader calldata _blobHeader,
        EigenDARollupUtils.BlobVerificationProof calldata _blobVerificationProof
    ) external onlyRole(SETTER_ROLE) {
        // if (projects[projectID].exists) {
        //     require(block.timestamp - readStorageDetail(projectID).lastUpdatedTimestamp > 90 days, "ProjectStorageVerifier: project already updated within 90 days");
        // }

        setStorageDetail(
            _blobHeader, 
            _blobVerificationProof, 
            projectID
        );

        // projects[projectID] = ProjectStore({
        //     exists: true,
        //     lastUpdatedHeadCID: lastUpdatedHeadCID
        // });
        projects[projectID] = true;
    }


    function verifyProjectStorageProof(string memory projectID) 
        external 
        view
    {
        require(projects[projectID], "ProjectStorageVerifier: invalid project");
        verifyAttestation(projectID);
    }


    function readProjectStorageProof(string calldata projectID) 
        external 
        view 
        returns (FullStore memory) 
    {
        // return FullStore({
        //     projectStore: projects[projectID],
        //     storageDetail: readStorageDetail(projectID)
        // });
        return FullStore({
            exists: projects[projectID],
            storageDetail: readStorageDetail(projectID)
        });
    }

}