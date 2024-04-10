# EigenDA Exploration -- Holesky
This repository contains exploratory work around the use of EigenDA as a data availability solution for IPFS systems. This setup is intended for the Holesky testnet.

### Prerequisites:
* [Install Conda](https://docs.anaconda.com/free/distro-or-miniconda/)
* [Install Go](https://go.dev/doc/install)
* [Install Ipfs](https://docs.ipfs.tech/install/command-line/#install-official-binary-distributions)

If deploying new smart contracts:
<!-- * [Install npm](https://github.com/nvm-sh/nvm?tab=readme-ov-file#installing-and-updating)
* [Install Hardhat](https://hardhat.org/hardhat-runner/docs/getting-started#installation) -->
* [Install Foundry and Foundryup](https://book.getfoundry.sh/getting-started/installation)

## Testing
* To test the Hello World script, run the following:
```
    mkdir eigenda-setup && cd eigenda-setup
    git clone https://github.com/dmp267/eigenda-exploration.git
    git clone https://github.com/Layr-Labs/eigenda.git

    conda env create -f eigenda-exploration/holesky/eigenda.env.yml && conda activate eigenda-exploration

    cd eigenda
    make build
    cd ../eigenda-exploration/holesky

    python hello_world.py
```

* To deploy the verifier smart contract, obtain a [Holesky RPC URL](https://chainlist.org/chain/17000) and the private key of an Ethereum wallet with a sufficient (>=0.1) HolETH balance and run the following:
```
    cd foundry
    forge install --no-git Layr-Labs/eigenlayer-contracts Layr-Labs/eigenlayer-middleware Layr-Labs/eigenda
    forge build
    forge test
    forge create --rpc-url $RPC_URL \
        --private-key $PRIVATE_KEY \
        --etherscan-api-key $ETHERSCAN_API_KEY \
        --verify \
        src/BlobVerifier.sol
```
