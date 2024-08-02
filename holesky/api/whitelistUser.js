// const { ethers } = require('ethers');
// const fs = require('fs');
// const path = require('path');
import { ethers } from 'ethers';
import fs from 'fs';
import path from 'path';
const abiPath = path.resolve(process.cwd(), 'backend/abi', 'CarbonMonitoringVerifier.json');
const abi = JSON.parse(fs.readFileSync(abiPath, 'utf8')).abi;

const contractAddress = '0x84cC6e1103B34f5A6298552f969AaFe1c5F78EEf';
const providerUrl = process.env.PROVIDER_URL;
const privateKey = process.env.PRIVATE_KEY;


export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { address } = req.body;
    
    if (!ethers.isAddress(address)) {
      return res.status(400).json({ error: 'Invalid Ethereum address' });
    }

    const provider = new ethers.JsonRpcProvider(providerUrl);
    const wallet = new ethers.Wallet(privateKey, provider);
    const contract = new ethers.Contract(contractAddress, abi, wallet);

    const tx = await contract.whitelistUser(address);
    const receipt = await tx.wait();

    res.status(200).json({ success: true, transactionHash: receipt.transactionHash });
  } catch (error) {
    console.error('Error calling whitelistUser:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
}

// curl -H "Content-Type: application/json" -d '{"address": "0x9a15e32290A9C2C01f7C8740B4484024aC92F2a1"}' https://vercel-functions-test-wine.vercel.app/api/whitelistUser | jq