# EigenDA Exploration -- Holesky

* [Register your operator to EigenLayer](https://github.com/Layr-Labs/eigenlayer-cli/blob/master/README.md)

    0. Add Holesky to Metamask manually:
    ```
        Network name:           Ethereum Holesky
        New RPC URL:            https://ethereum-holesky-rpc.publicnode.com
        Chain ID:               17000
        Currency symbol:        ETH
        Block explorer URL:     https://holesky.beaconcha.in/
    ```
    1. Generate a password and use it to create the operator keys
    ```
        export PASSWORD=<your_password>
        # example key names
        export ECDSA_KEYNAME="ecdsa-key"
        export BLS_KEYNAME="bls-key"
        # create operator keys and encrypt with password
        echo $PASSWORD | eigenlayer operator keys create --key-type ecdsa $ECDSA_KEYNAME
        echo $PASSWORD | eigenlayer operator keys create --key-type bls $BLS_KEYNAME
    ```
    2. To get the address and location of your ECDSA key run 
    ```
        eigenlayer operator keys list
    ```
    3. Obtain at least 1 HolETH from a [faucet](https://docs.eigenlayer.xyz/eigenlayer/restaking-guides/restaking-user-guide/stage-2-testnet/obtaining-testnet-eth-and-liquid-staking-tokens-lsts#obtain-holesky-eth-aka-holeth-via-a-faucet) and transfer to the address from step 2
    4. Run the command below and provide details from step 2 as well as an RPC URL from [here](https://chainlist.org/chain/17000) or the one added to Metamask above
    ```
        eigenlayer operator config create
    ```
    5. Update the metadata URL in the `operator.yaml` file with the link to the raw `metadata.json` hosted on Github
    6. Run the command below and provide the password from step 1
    ```
        eigenlayer operator register operator.yaml
    ```
* Prepare Local EigenDA files
    
    1. Clone [this operator repo](https://github.com/Layr-Labs/eigenda-operator-setup/tree/master/) and execute the following commands:
    ```
        git clone https://github.com/Layr-Labs/eigenda-operator-setup.git
        cd eigenda-operator-setup/holesky
        cp .env.example .env
    ```
    2. Create local folders which are required by EigenDA in the next step
    ```
        mkdir -p $HOME/.eigenlayer/eigenda/holesky/logs
        mkdir -p $HOME/.eigenlayer/eigenda/holesky/db
    ```
    3. Manually update the .env file downloaded in the steps above. Modify all sections marked with TODO to match your environment




