import { create } from 'ipfs-http-client';

export const config = {
  api: {
    bodyParser: false,
  },
};

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    const auth =
      'Basic ' +
      Buffer.from(process.env.INFURA_PROJECT_ID + ':' + process.env.INFURA_PROJECT_SECRET).toString('base64');

    const client = create({
      host: 'ipfs.infura.io',
      port: 5001,
      protocol: 'https',
      headers: {
        authorization: auth,
      },
    });

    const formidable = require('formidable');
    const form = new formidable.IncomingForm();

    form.parse(req, async (err, fields, files) => {
      if (err) {
        return res.status(500).json({ error: 'Error parsing the file' });
      }

      const file = files.file;

      if (!file) {
        return res.status(400).json({ error: 'No file uploaded' });
      }
      
      const fs = require('fs');
      const fileContent = fs.readFileSync(file.filepath);

      const added = await client.add(fileContent);
      res.status(200).json({ cid: added.cid.toString() });
    });
  } catch (error) {
    console.error('Error uploading file to IPFS:', error);
    res.status(500).json({ error: 'Failed to upload file to IPFS' });
  }
};