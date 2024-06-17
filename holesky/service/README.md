# EigenDA Exploration : Holesky Demo Walkthrough

For now the app can be run as a standalone service or as an external adapter served by Chainlink Operators.

## Standalone
For the standalone version, the service supports the following three request types:

### Query
This request type accepts a KML file defining the boundaries of a region for which to retrieve carbon data. 

This returns the most recently published measurements<sup>*</sup> for above-ground biomass in tonnes per hectare (x 1/1000) and deforestation in square decameters per hectare (x 1/1000) aggregated over the specified region.

```
# example request
curl -X POST -F "file=@data/projects/852.kml" http://127.0.0.1:5000/query
```
```json
# example response
{
    "agb": {
        "data": 638312500,
        "head_cid": "bafyreifuh56spzd6rpn3yldxcrfibcjducrjm7ikmbf62s6c3txfpm366m",
        "timestamp_ms": 1672549200000,
        "unit": "tonne/hectare / 1000"
    },
    "deforestation": {
        "data": 9926329,
        "head_cid": "bafyreicv7xwwcz4qdo3lz4okefdplq47b5mcs32oiragaxbchtjwya57je",
        "timestamp (ms)": 1672549200000,
        "unit": "decameter**2/hectare / 1000"
    },
    "status": "success"
}
```
<sup>*</sup>Above-ground biomass and deforestation data provided by dClimate and CYCLOPS models

### Store
This request type accepts a data blob and disperses it to EigenDA's data availability network and verifies the resulting proof in a smart contract. These requests also require a project name to index the project storage details in the smart contract, and a CID to track the head of the datasets on IPFS at the time of storage. In the future, the Above-ground biomass and Deforestation datasets will be combined, so for now only the AGB head CID is specified on-chain.

This returns the proof data provided by the EigenDA disperser after confirmation of data availability. This data is also persisted on-chain at the same time for backup retrieval. Reconstruction of both the full blob header and blob verification proof is necessary to verify data availibility. Transaction receipts for storing proof details on-chain are optionally available for return.

```
# example request
curl -X POST -H "Content-Type: application/json" -d '{
  "project_name": "project-852-holesky",
  "cid": "bafyreifuh56spzd6rpn3yldxcrfibcjducrjm7ikmbf62s6c3txfpm366m",
  "data": {
    "agb": {
      "data": 638312500,
      "timestamp_ms": 1672549200000,
      "unit": "tonne/hectare / 1000"
    },
    "deforestation": {
      "data": 9926329,
      "head_cid": "bafyreicv7xwwcz4qdo3lz4okefdplq47b5mcs32oiragaxbchtjwya57je",
      "timestamp (ms)": 1672549200000,
      "unit": "decameter**2/hectare / 1000"
    }
  }
}' http://127.0.0.1:5000/store
```
```json
# example response
{
    "blob_header": {
        "commitment": {
            "x": 17085185418938184936394716208061724156759708588531044027077035541350114936503,
            "y": 19070878187577835227273245729636004753451532273749094128979189077629162650260
        },
        "data_length": 17,
        "blob_quorum_params": [
            {
                "quorum_number": 0,
                "adversary_threshold_percentage": 33,
                "confirmation_threshold_percentage": 55,
                "chunk_length": 1
            },
            {
                "quorum_number": 1,
                "adversary_threshold_percentage": 33,
                "confirmation_threshold_percentage": 55,
                "chunk_length": 1
            }
        ]
    },
    "blob_verification_proof": {
        "batch_id": 19659,
        "blob_index": 627,
        "batch_metadata": {
            "batch_header": {
                "batch_root": "fc35808bdb6245cf118ec63f7684d8ca64bb9872891c6f79d096cb8e9c22a2e2",
                "quorum_numbers": "0001",
                "quorum_signed_percentages": "5659",
                "reference_block_number": 1756069
            },
            "signatory_record_hash": "1f7b66861bb309f1ccccb9843653e64a0caed82b1687e5f11f69cb19d67ff9a0",
            "fee": "00",
            "confirmation_block_number": 1756193,
            "batch_header_hash": "950f78584983de7444922fc1b2802d0689225e0615bfc2916ecbf1d4fcf6a631"
        },
        "inclusion_proof": "72fc22cba8e811722c1e49a7d8f8b72f7e140daa26045703d60f54aac5c9d7c6220244d2b7aa2da484cb293cfc76ef94b288e0f34bf5c0c4aa3921f95b84829fe60020c66581d0239f1f60391e17edc1b5aa198604fa166b76c8873363cd1e9edafd28f4188b5bb847498dbcedaffd9439cd2d355cfdfa9e4789aa920225082880d54b9b7657ca6f3b421a45097c1898ae48c777d3fcfa375b513096d836dfd4c8ea9a8fae56060f64f7d737906007a50d82521473722c017223d82ee6b900e90b7bde86d43078e6494d1a5209f0c44760ba1e7ac9090508dc7af669c7e689b9e8330850a7ab853a5ca4127b7f272130fc5140d8ff85ba7ae752f56cce1a2013ba7d045d217902b1b289d45fe370e976a0437392f8001dd72bb1b6cf126e81afccd4d54c308374ddb8927e0d83a58aa7c509ef01841ff3ec5feafbbbde0d77fecca587eba673050e15ba42f6dd10c59b6743a8d93e34eb53da1e4456c209ffd2",
        "quorum_indexes": "0001"
    }
}
```
```json
# example additional response with transaction receipt for on-chain storage
{
    "blockHash": "dd674a79977aafc3327a819997f200da2653f6638c9d42ef1f5649536174acc0", "blockNumber": 1756196, 
    "contractAddress": "null", 
    "cumulativeGasUsed": 3738884, 
    "effectiveGasPrice": 1148047598, 
    "from": "0x9a15e32290A9C2C01f7C8740B4484024aC92F2a1", 
    "gasUsed": 949334, 
    "logs": [], 
    "logsBloom": "00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000", 
    "status": 1, 
    "to": "0x434a156aA863c66FAd723a7e3fb68C317DF5f0b7", 
    "transactionHash": "17e1c4dcbf9b9774f9e183423c8fa2d2940e6277e0bb6dcc9d3c4cb2bba1e953", 
    "transactionIndex": 21, 
    "type": 2
}
```

### Retrieve
This request type accepts a project name and retrieves the associated data from the EigenDA network.

This returns the data stored on EigenDA.

```
# example request
curl -X GET http://127.0.0.1:5000/retrieve/project-852-holesky
```
```json
# example response
{
    "agb": {
        "data": 638312500,
        "timestamp_ms": 1672549200000,
        "unit": "tonne/hectare / 1000"
    },
    "deforestation": {
        "data": 9926329,
        "head_cid": "bafyreicv7xwwcz4qdo3lz4okefdplq47b5mcs32oiragaxbchtjwya57je",
        "timestamp (ms)": 1672549200000,
        "unit": "decameter**2/hectare / 1000"
    }
}
```

## Chainlink (WIP)
...

