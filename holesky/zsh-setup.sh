# install eigenlayer-cli and add to zsh path
curl -sSfL https://raw.githubusercontent.com/layr-labs/eigenlayer-cli/master/scripts/install.sh | sh -s
export PATH=$PATH:~/bin >> ~/.zprofile
source ~/.zprofile

# example key names
export ECDSA_KEYNAME="ecdsa-key"
export BLS_KEYNAME="bls-key"

# create operator keys and encrypt with password
echo $PASSWORD | eigenlayer operator keys create --key-type ecdsa $ECDSA_KEYNAME
echo $PASSWORD | eigenlayer operator keys create --key-type bls $BLS_KEYNAME

# set environment variables including holesky rpc
export ECDSA_ADDRESS=$(eigenlayer operator keys list | grep "Address: " | sed "s/^Address: //")
export ECDSA_PATH=$(eigenlayer operator keys list | grep "Key location: " | tail -n 1 | sed "s/^Key location: //")
export RPC_URL="https://ethereum-holesky-rpc.publicnode.com"

# Register operator
eigenlayer operator config create
# inputs:
#     y
#     $ECDSA_ADDRESS
#     $ECDSA_ADDRESS
#     $RPC_URL
#     $ECDSA_PATH
#     holesky

# Additional steps:
# 1. Add Holesky to Metamask manually
# inputs:
#     Ethereum Holesky
#     https://ethereum-holesky-rpc.publicnode.com
#     17000
#     ETH
#     https://holesky.beaconcha.in/
# 2. Fund operator.yaml address with 1 holETH
# 3. Upload .png logo to Github
# 4. Add logo url to metadata.json and upload to Github
# 5. Add metadata.json url to operator.yaml

# eigenlayer operator register operator.yaml
# $PASSWORD