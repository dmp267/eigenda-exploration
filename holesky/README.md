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
