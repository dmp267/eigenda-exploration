// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "src/BlobVerifier.sol";


contract CarbonDataVerifier is BlobVerifier {

    // storage details for verification for agb-quarterly and deforestation-quarterly datasets
    struct DatasetStore {
        bool initialized;
        uint256 lastUpdatedTimestamp;
        string lastUpdatedHeadCID;
    }

    struct FullStore {
        DatasetStore datasetStore;
        StorageDetail storageDetail;
    }

    mapping(string => DatasetStore) public datasets;


    constructor(address owner) BlobVerifier(owner) {
        // supported datasets
        datasets["agb-quarterly"] = DatasetStore({
            initialized: true,
            lastUpdatedTimestamp: 0,
            lastUpdatedHeadCID: ""
        });
        datasets["deforestation-quarterly"] = DatasetStore({
            initialized: true,
            lastUpdatedTimestamp: 0,
            lastUpdatedHeadCID: ""
        });
    }


    function updateDataset(
        string calldata datasetName,
        string calldata lastUpdatedHeadCID,
        ModifiedBlobHeader calldata _blobHeader,
        EigenDARollupUtils.BlobVerificationProof calldata _blobVerificationProof
    ) external onlyOwner {
        require(datasets[datasetName].initialized, "CarbonDataVerifier: invalid dataset");

        uint lastUpdated = datasets[datasetName].lastUpdatedTimestamp;
        if (lastUpdated != 0) {
            require(block.timestamp - lastUpdated > 90 days, "CarbonDataVerifier: dataset already updated within 90 days");
        }
        setStorageDetail(
            _blobHeader, 
            _blobVerificationProof, 
            lastUpdatedHeadCID
        );

        datasets[datasetName] = DatasetStore({
            initialized: true,
            lastUpdatedTimestamp: block.timestamp,
            lastUpdatedHeadCID: lastUpdatedHeadCID
        });
    }


    function verifyDataset(string calldata datasetName) 
        external 
        view
    {
        require(datasets[datasetName].initialized && datasets[datasetName].lastUpdatedTimestamp > 0, "CarbonDataVerifier: invalid dataset");
        verifyAttestation(datasets[datasetName].lastUpdatedHeadCID);
    }


    function readDatasetStorageDetails(string calldata datasetName) 
        external 
        view 
        returns (FullStore memory) 
    {
        return FullStore({
            datasetStore: datasets[datasetName],
            storageDetail: readStorageDetail(datasetName)
        });
    }


    function addSupportedDataset(string calldata _supportedDataset) external onlyOwner {
        require(!datasets[_supportedDataset].initialized, "CarbonDataVerifier: dataset already supported");
        datasets[_supportedDataset] = DatasetStore({
            initialized: true,
            lastUpdatedTimestamp: 0,
            lastUpdatedHeadCID: ""
        });
    }
}