# EigenDA Exploration
This repository contains exploratory work around the use of EigenDA as a data availability solution for IPFS systems. Currently a setup is provided for use with the Holesky testnet.


The provided setup defines a Flask app which, alongside a local IPFS node, can download data that is available on IPFS, upload that data to the EigenDA network for storage persistentence, and verify on-chain the provided attestations of the data's storage:


![diagram](holesky/public/eigenda-explore.jpg)


The README in the Holesky directory includes the instructions to run each part of the service.