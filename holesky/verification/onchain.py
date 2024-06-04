import os
import json
import datetime
from web3 import Web3

# CONSTANTS
PRIVATE_KEY = os.environ.get('PRIVATE_KEY', '0x00')
WALLET_ADDRESS = os.environ.get('WALLET_ADDRESS', '0x9a15e32290A9C2C01f7C8740B4484024aC92F2a1')
CONTRACT_ADDRESS = os.environ.get('CONTRACT_ADDRESS', '0xa510C89DD5DD60CDC9cB52E2524CBD28c22FC663') # TODO: update with new (temporary) contract address
RPC_URL = os.environ.get('RPC_URL', "https://ethereum-holesky-rpc.publicnode.com")
ABI = json.load(open('foundry/out/ProjectStorageVerifier.sol/ProjectStorageVerifier.json'))['abi']

web3 = Web3(Web3.HTTPProvider(RPC_URL))
chainId = web3.eth.chain_id
print(f'Connected to {RPC_URL} for chain {chainId}: {web3.is_connected()}')


def read_store_details(project_name: str):
    """
    Read the storage details of a carbon monitoring/management project from the smart contract.

    Parameters:
        project_name (str): The name of the project.

    Returns:
        dict: The storage details of the project.
    """
    contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)
    full_detail = contract.functions.readProjectStorageProof(project_name).call()
    project_store = full_detail[0]
    storage_detail = full_detail[1]
    result = {
        "last_updated_timestamp": datetime.fromtimestamp(int(storage_detail[0])),
        "last_updated_head_cid": datetime.fromtimestamp(int(project_store[0])),
        "blob_index": int(storage_detail[2][1]), 
        "batch_header_hash": storage_detail[1][2]
    }
    print(result)
    return result


def store_on_chain(project_name: str, cid: str, result: str):
    """
    Store the storage details of a carbon monitoring/management project on the smart contract.

    Parameters:
        project_name (str): The name of the project.
        cid (str): The IPFS CID of the head of the data associated with the project.
        result (dict): The storage details of the project.

    Returns:
        dict: The receipt of the transaction.
    """
    contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)

    params_list = result['blob_header']['blob_quorum_params']
    quorum_numbers = []
    adversary_threshold_percentages = []
    confirmation_threshold_percentages = []
    chunk_lengths = []
    for params in params_list:
        quorum_numbers.append(params['quorum_number'])
        adversary_threshold_percentages.append(params['adversary_threshold_percentage'])
        confirmation_threshold_percentages.append(params['confirmation_threshold_percentage'])
        chunk_lengths.append(params['chunk_length'])
    
    commitment_args = [result['blob_header']['commitment']['x'], result['blob_header']['commitment']['y']]

    blob_header_args = [commitment_args,
                        result['blob_header']['data_length'],
                        bytes.fromhex(result['blob_verification_proof']['batch_metadata']['batch_header_hash']),
                        quorum_numbers,
                        adversary_threshold_percentages,
                        confirmation_threshold_percentages,
                        chunk_lengths]

    batch__header_args = [bytes.fromhex(result['blob_verification_proof']['batch_metadata']['batch_header']['batch_root']),
                          bytes.fromhex(result['blob_verification_proof']['batch_metadata']['batch_header']['quorum_numbers']),
                          bytes.fromhex(result['blob_verification_proof']['batch_metadata']['batch_header']['quorum_signed_percentages']),
                          result['blob_verification_proof']['batch_metadata']['batch_header']['reference_block_number']]

    batch_metadata_args = [batch__header_args,
                           bytes.fromhex(result['blob_verification_proof']['batch_metadata']['signatory_record_hash']),
                           result['blob_verification_proof']['batch_metadata']['confirmation_block_number']]

    blob_verification_proof_args = [result['blob_verification_proof']['batch_id'],
                                    result['blob_verification_proof']['blob_index'],
                                    batch_metadata_args,
                                    bytes.fromhex(result['blob_verification_proof']['inclusion_proof']),
                                    bytes.fromhex(result['blob_verification_proof']['quorum_indexes'])]

    nonce = web3.eth.get_transaction_count(WALLET_ADDRESS)
    update_dataset = contract.functions.uploadProjectStorageProof(
        project_name,
        cid,
        blob_header_args, 
        blob_verification_proof_args).build_transaction({
            "chainId": chainId, 
            "from": WALLET_ADDRESS, 
            "nonce": nonce})
    
    signed_txn = web3.eth.account.sign_transaction(update_dataset, private_key=PRIVATE_KEY)
    send_txn = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    receipt = web3.eth.wait_for_transaction_receipt(send_txn)
    return receipt


def verify_on_chain(project_name: str):
    """
    Verify the storage details of a carbon monitoring/management project on the smart contract.

    Parameters:
        project_name (str): The name of the project.

    Returns:
        bool: The verification status of the project.
    """
    contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)
    verification = contract.functions.verifyDataset(project_name).call()
    print(f'Verification for dataset {project_name}: {verification}')
    return verification
