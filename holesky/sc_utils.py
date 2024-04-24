import os
import json
from web3 import Web3

PRIVATE_KEY = os.environ.get('PRIVATE_KEY', '0x00')
WALLET_ADDRESS = os.environ.get('WALLET_ADDRESS', '0x9a15e32290A9C2C01f7C8740B4484024aC92F2a1')
CONTRACT_ADDRESS = os.environ.get('CONTRACT_ADDRESS', '0x27C624d5aCF1b351970E1D6277A3656a4DB7A108')
RPC_URL = os.environ.get('RPC_URL', "https://ethereum-holesky-rpc.publicnode.com")
ABI = json.load(open('foundry/out/BlobVerifier.sol/BlobVerifier.json'))['abi']


web3 = Web3(Web3.HTTPProvider(RPC_URL))
chainId = web3.eth.chain_id
print(f'Connected to {RPC_URL} for chain {chainId}: {web3.is_connected()}')


def get_store_details(cid: str):
    contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)
    full_detail = contract.functions.readStorageDetail(cid).call()
    blob_index = full_detail[1][1]
    batch_header_hash = full_detail[0][2]
    result = {"blob_index": int(blob_index), "batch_header_hash": batch_header_hash}
    print(result)
    return result


def store_on_chain(cid: str, result: str):
    receipts = []
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
    
    blob_header_args = [result['blob_header']['data_length'], 
                        result['blob_header']['commitment']['x'], 
                        result['blob_header']['commitment']['y'], 
                        bytes.fromhex(result['blob_verification_proof']['batch_metadata']['batch_header_hash']),
                        quorum_numbers,
                        adversary_threshold_percentages,
                        confirmation_threshold_percentages,
                        chunk_lengths,
                        cid]

    nonce = web3.eth.get_transaction_count(WALLET_ADDRESS)
    set_blob_header = contract.functions.setBlobHeader(*blob_header_args).build_transaction({"chainId": chainId, "from": WALLET_ADDRESS, "nonce": nonce})

    signed_txn = web3.eth.account.sign_transaction(set_blob_header, private_key=PRIVATE_KEY)
    send_txn = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    receipt = web3.eth.wait_for_transaction_receipt(send_txn)
    receipts.append(receipt)

    batch_metadata_args = [bytes.fromhex(result['blob_verification_proof']['batch_metadata']['signatory_record_hash']),
                           result['blob_verification_proof']['batch_metadata']['confirmation_block_number'],
                           bytes.fromhex(result['blob_verification_proof']['batch_metadata']['batch_header']['batch_root']),
                           result['blob_verification_proof']['batch_metadata']['batch_header']['reference_block_number'],
                           bytes.fromhex(result['blob_verification_proof']['batch_metadata']['batch_header']['quorum_numbers']),
                           bytes.fromhex(result['blob_verification_proof']['batch_metadata']['batch_header']['quorum_signed_percentages']),
                           cid]

    nonce = web3.eth.get_transaction_count(WALLET_ADDRESS)
    set_batch_metadata = contract.functions.setBatchMetadata(*batch_metadata_args).build_transaction({"chainId": chainId, "from": WALLET_ADDRESS, "nonce": nonce})
    
    signed_txn = web3.eth.account.sign_transaction(set_batch_metadata, private_key=PRIVATE_KEY)
    send_txn = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    receipt = web3.eth.wait_for_transaction_receipt(send_txn)
    receipts.append(receipt)

    blob_verification_proof_args = [result['blob_verification_proof']['batch_id'],
                                    result['blob_verification_proof']['blob_index'],
                                    bytes.fromhex(result['blob_verification_proof']['inclusion_proof']),
                                    bytes.fromhex(result['blob_verification_proof']['quorum_indexes']),
                                    cid]

    nonce = web3.eth.get_transaction_count(WALLET_ADDRESS)
    set_blob_verification_proof = contract.functions.setBlobVerificationProof(*blob_verification_proof_args).build_transaction({"chainId": chainId, "from": WALLET_ADDRESS, "nonce": nonce})
    
    signed_txn = web3.eth.account.sign_transaction(set_blob_verification_proof, private_key=PRIVATE_KEY)
    send_txn = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    receipt = web3.eth.wait_for_transaction_receipt(send_txn)
    receipts.append(receipt)

    return receipts


def verify_on_chain(cid: str):
    contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)
    verification = contract.functions.verifyAttestation(cid).call()
    print(f'Verification for CID {cid}: {verification}')
    return verification
