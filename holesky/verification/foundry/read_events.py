import json
from web3 import Web3
# from eth_abi import decode_abi


w3 = Web3(Web3.HTTPProvider('https://ethereum-holesky-rpc.publicnode.com'))


contract_address = '0x49D86501826a44E41faBE8F53AC1D3CD395caac9'
with open('./out/CarbonMonitoringVerifier.sol/CarbonMonitoringVerifier.json') as abi_file:
    contract_abi = json.load(abi_file)['abi']

contract = w3.eth.contract(address=contract_address, abi=contract_abi)

print(contract_abi)

disperser_event_abi = next((abi for abi in contract_abi if abi['type'] == 'event' and abi['name'] == 'RequestDisperseDataFulfilled'), None)

if not disperser_event_abi:
    print('Event not found')
    exit()

event_signature_hash = w3.keccak(text=disperser_event_abi['name'] + '(' + ','.join([param['type'] for param in disperser_event_abi['inputs']]) + ')').hex()

latest_block = w3.eth.get_block('latest')['number']

event_filter = w3.eth.filter({
    'fromBlock': latest_block - 1000,
    'toBlock': latest_block,
    'address': contract_address,
    'topics': [event_signature_hash]
})

logs = event_filter.get_all_entries()

def read_from_mapping(mapping_name, key):
    return contract.functions[mapping_name](key).call()


if logs:
    latest_log = logs[-1]

    decoded_log = contract.events.RequestDisperseDataFulfilled().process_log(latest_log)

    print('Event data:', decoded_log['args'])
    dispersal_request = read_from_mapping('dispersalRequests', "852-monitor:carbon@verifier.com")#decoded_log['args']['requestId'])
    print('Dispersion request:', dispersal_request)