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

## Examples
* To test the Hello World script, run the following:
```
    mkdir eigenda-setup && cd eigenda-setup
    git clone https://github.com/dmp267/eigenda-exploration.git
    git clone https://github.com/Layr-Labs/eigenda.git

    conda env create -f eigenda-exploration/holesky/eigenda.env.yml && conda activate eigenda-exploration

    cd eigenda
    make build
    cd ../eigenda-exploration/holesky/attestations/examples

    python hello_world.py
```
If you observe issues with imports move the example file to this directory and retry.

* To test the verifier smart contract, obtain a [Holesky RPC URL](https://chainlist.org/chain/17000) and run the following:
```
    cd foundry
    forge install --no-git Layr-Labs/eigenlayer-contracts Layr-Labs/eigenlayer-middleware Layr-Labs/eigenda
    forge build
    anvil --fork-url $RPC_URL
    # in another window
    forge script script/BlobVerification.s.sol --rpc-url http://127.0.0.1:8545
```


## Components
* To run the IPFS node, assuming you have initialized the necessary IPFS directories, run
```
ipfs daemon
```
* To run the Flask app, assuming you have activated the Conda environment above, run
```
python -m flask app.py
```
* To deploy the verifier smart contract, assuming you have an RPC URL, an [Etherscan API key](https://etherscan.io/), and a >0.1 HolETH balance, run
```
forge create --rpc-url $RPC_URL \
        --private-key $PRIVATE_KEY \
        --etherscan-api-key $ETHERSCAN_API_KEY \
        --verify \
        src/BlobVerifier.sol
```
