# EigenDA Exploration -- Holesky
This repository contains instructions on how to run each of the components for this service.


### Prerequisites:
* [Install Conda](https://docs.anaconda.com/free/distro-or-miniconda/)
* [Install Go](https://go.dev/doc/install)
* [Install Ipfs](https://docs.ipfs.tech/install/command-line/#install-official-binary-distributions)

If deploying new smart contracts:
<!-- * [Install npm](https://github.com/nvm-sh/nvm?tab=readme-ov-file#installing-and-updating)
* [Install Hardhat](https://hardhat.org/hardhat-runner/docs/getting-started#installation) -->
* [Install Foundry and Foundryup](https://book.getfoundry.sh/getting-started/installation)

## Components
* To run the IPFS node, assuming you have initialized the necessary IPFS directories, run
```
ipfs daemon
```
* To run the main app, assuming you have activated the Conda environment above, run
```
python app.py
```
* To deploy the verifier smart contract, assuming you have an RPC URL, an [Etherscan API key](https://etherscan.io/), and a >0.1 HolETH balance, run
```
# if the EigenDARollupUtils library has not already been deployed then deploy it with

forge create --rpc-url $RPC_URL \
        --private-key $PRIVATE_KEY \
        --etherscan-api-key $ETHERSCAN_API_KEY \
        --verify \
        lib/eigenda/contracts/src/libraries/EigenDARollupUtils.sol:EigenDARollupUtils

# get the library's DEPLOYED_ADDRESS, in this case we have already deployed the library on Holesky at 0x53D155A342265094898742e42258beBe6d0f58f6. Now run

forge create --rpc-url $RPC_URL \
        --constructor-args $WALLET_ADDRESS \
        --private-key $PRIVATE_KEY \
        --etherscan-api-key $ETHERSCAN_API_KEY \
        --verify \
        src/ProjectStorageVerifier.sol:ProjectStorageVerifier \
        --libraries lib/eigenda/contracts/src/libraries/EigenDARollupUtils.sol:EigenDARollupUtils:$DEPLOYED_ADDRESS
```

## Examples
* To test the Carbon script, which pulls a carbon dataset from IPFS, disperses it to EigenDA, and stores and verifies the proof on-chain, run the following:
```
    mkdir eigenda-setup && cd eigenda-setup
    git clone https://github.com/dmp267/eigenda-exploration.git
    git clone https://github.com/Layr-Labs/eigenda.git

    conda env create -f eigenda-exploration/holesky/eigenda.env.yml && conda activate eigenda-exploration

    cd eigenda
    make build
    cd ../eigenda-exploration/holesky

    python demo.py
```
* To test the verifier smart contract, obtain a [Holesky RPC URL](https://chainlist.org/chain/17000) and run the following:
```
    cd foundry
    forge install --no-git Layr-Labs/eigenlayer-contracts Layr-Labs/eigenlayer-middleware Layr-Labs/eigenda OpenZeppelin/openzeppelin-contracts
    forge build
    anvil --fork-url $RPC_URL
    # in another window
    forge script script/ProjectStorageDeployAndVerify.s.sol --rpc-url http://127.0.0.1:8545
```
