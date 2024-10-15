import dotenv from "dotenv";
import path from "path";

import { fileURLToPath } from 'url';

// Get __dirname equivalent in ES module
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config();

export interface IEnvVariables {
  backendUrl: string;
  ilpUrl: string;
  walletAddressUrl: string;
  keyID: string;
  privateKeyID: string;
}

export const getEnviromentVariables = (): IEnvVariables => {
  const variables = {
    backendUrl: /*process.env.BACKEND_URL || */"http://localhost:3000",
    ilpUrl: /*process.env.ILP_URL || */"http://localhost:3001",
    walletAddressUrl: "https://ilp.rafiki.money/stokvel_app",//process.env.WALLET_ADDRESS_URL || "",
    keyID: "853aa509-9d78-4354-96d1-4236cbe1236e",//process.env.KEY_ID || "",
    privateKeyID: path.resolve(__dirname, './private.key'),//process.env.PRIVATE_KEY_ID || "",      // Ensure the correct file path
  };

  return variables;
};
