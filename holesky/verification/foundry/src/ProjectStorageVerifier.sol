// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "./BlobVerifier.sol";


contract ProjectStorageVerifier is BlobVerifier {

    // storage details for carbon monitoring projects
    struct ProjectStore {
        string lastUpdatedHeadCID;
        // coords?
    }

    // return type for readProjectStorageDetails
    struct FullStore {
        ProjectStore projectStore;
        StorageDetail storageDetail;
    }

    mapping(string => ProjectStore) public projects;


    constructor(address owner) BlobVerifier(owner) {
    }


    function uploadProjectStorageProof(
        string calldata projectName,
        string calldata lastUpdatedHeadCID,
        ModifiedBlobHeader calldata _blobHeader,
        EigenDARollupUtils.BlobVerificationProof calldata _blobVerificationProof
    ) external onlyOwner {
        uint lastUpdated = readStorageDetail(projectName).lastUpdatedTimestamp;
        if (lastUpdated != 0) {
            require(block.timestamp - lastUpdated > 90 days, "ProjectStorageVerifier: project already updated within 90 days");
        } 

        setStorageDetail(
            _blobHeader, 
            _blobVerificationProof, 
            projectName
        );

        projects[projectName] = ProjectStore({
            lastUpdatedHeadCID: lastUpdatedHeadCID
        });
    }


    function verifyProjectStorageProof(string calldata projectName) 
        external 
        view
    {
        require(readStorageDetail(projectName).lastUpdatedTimestamp > 0, "ProjectStorageVerifier: invalid project");
        verifyAttestation(projects[projectName].lastUpdatedHeadCID);
    }


    function readProjectStorageProof(string calldata projectName) 
        external 
        view 
        returns (FullStore memory) 
    {
        return FullStore({
            projectStore: projects[projectName],
            storageDetail: readStorageDetail(projectName)
        });
    }

}