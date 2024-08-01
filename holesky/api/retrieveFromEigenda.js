const { ethers } = require('ethers');
const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');
const path = require('path');
const fs = require('fs');

// CONSTANTS
const BYTES_PER_SYMBOL = 32;
const DISPERSER = "disperser-holesky.eigenda.xyz:443";

const VERIFIER_CONTRACT_ADDRESS = process.env.VERIFIER_CONTRACT_ADDRESS || '0x8032b4DBa3779B6836B4C69203bB1d3b4f92908B';
const RPC_URL = process.env.RPC_URL || "https://ethereum-holesky-rpc.publicnode.com";
const ABI = JSON.parse(fs.readFileSync(path.join(__dirname, 'abi/ProjectStorageVerifier.sol/ProjectStorageVerifier.json'))).abi;

// Setup gRPC client
const protoPath = path.resolve(__dirname, './proto/disperser/disperser.proto');
const packageDefinition = protoLoader.loadSync(protoPath, { keepCase: true, longs: String, enums: String, defaults: true, oneofs: true });
const disperserProto = grpc.loadPackageDefinition(packageDefinition).protobufs.disperser;

const grpcClient = new disperserProto.Disperser(DISPERSER, grpc.credentials.createSsl());

// Setup Web3 provider
const provider = new ethers.providers.JsonRpcProvider(RPC_URL);
const contract = new ethers.Contract(VERIFIER_CONTRACT_ADDRESS, ABI, provider);

function removeEmptyByteFromPaddedBytes(data) {
    const parseSize = BYTES_PER_SYMBOL;
    const dataSize = data.length;
    const dataLen = Math.ceil(dataSize / parseSize);
    
    const putSize = BYTES_PER_SYMBOL - 1;
    const validData = Buffer.alloc(dataLen * putSize);
    let validLen = validData.length;

    for (let i = 0; i < dataLen; i++) {
        let start = i * parseSize + 1;
        let end = (i + 1) * parseSize;
        if (end > dataSize) {
            end = dataSize;
            validLen = end - start + i * putSize;
        }
        data.copy(validData, i * putSize, start, end);
    }
    return validData.subarray(0, validLen);
}

function decodeRetrieval(data) {
    const reconvertedData = removeEmptyByteFromPaddedBytes(data);
    return reconvertedData.toString("utf-8");
}

function retrieveFromEigenDA(batchHeaderHash, blobIndex) {
    return new Promise((resolve, reject) => {
        const retrieveRequest = { batch_header_hash: batchHeaderHash, blob_index: blobIndex };
        grpcClient.RetrieveBlob(retrieveRequest, (error, response) => {
            if (error) {
                return reject(error);
            }
            const storedData = Buffer.from(response.data);
            const result = decodeRetrieval(storedData);
            resolve(result);
        });
    });
}

async function readStoreDetails(projectId) {
    const fullDetail = await contract.readProjectStorageProof(projectId);
    const storageDetail = fullDetail[1];
    return {
        last_updated_timestamp: new Date(storageDetail[0] * 1000),
        blob_index: Number(storageDetail[2][1]),
        batch_header_hash: storageDetail[1][2]
    };
}

async function verifyOnChain(projectId) {
    return await contract.verifyProjectStorageProof(projectId);
}

async function retrieveData(id) {
    await verifyOnChain(id);
    const storeDetails = await readStoreDetails(id);
    const data = await retrieveFromEigenDA(storeDetails.batch_header_hash, storeDetails.blob_index);
    return JSON.parse(data);
}

// Vercel Serverless Function handler
export default async function handler(req, res) {
    if (req.method !== 'POST') {
        res.status(405).json({ error: 'Method not allowed' });
        return;
    }

    let requestData;
    try {
        requestData = JSON.parse(req.body);
    } catch (error) {
        res.status(400).json({ error: 'Invalid JSON' });
        return;
    }

    const projectId = requestData.project_id || '';
    if (projectId === '') {
        res.status(400).json({ error: "project_id not provided" });
        return;
    }

    try {
        const result = await retrieveData(projectId);
        res.status(200).json(result);
    } catch (error) {
        console.error('Error retrieving data:', error);
        res.status(500).json({ error: 'Failed to retrieve data' });
    }
};