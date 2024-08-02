// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../contracts/BlobVerifier.sol";
import "../interfaces/IProjectStorageVerifier.sol";

// CURRENT DEPLOYED ADDRESS: 0x8032b4DBa3779B6836B4C69203bB1d3b4f92908B
contract ProjectStorageVerifier is IProjectStorageVerifier, BlobVerifier {

    mapping(string => bool) public projects;


    constructor(address owner) BlobVerifier(owner) {}


    function uploadProjectStorageProof(
        string calldata projectID,
        ModifiedBlobHeader calldata _blobHeader,
        EigenDARollupUtils.BlobVerificationProof calldata _blobVerificationProof
    ) external onlyRole(SETTER_ROLE) {

        setStorageDetail(
            _blobHeader, 
            _blobVerificationProof, 
            projectID
        );

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
        return FullStore({
            exists: projects[projectID],
            storageDetail: readStorageDetail(projectID)
        });
    }


    // function updateProjectStorageId(string calldata projectID, string calldata newProjectID) 
    //     external 
    //     onlyRole(SETTER_ROLE) 
    // {
    //     require(projects[projectID], "ProjectStorageVerifier: invalid project");
    //     require(!projects[newProjectID], "ProjectStorageVerifier: new project already exists");
    //     updateStorageId(projectID, newProjectID);
    //     projects[newProjectID] = true;
    //     projects[projectID] = false;
    // }

}