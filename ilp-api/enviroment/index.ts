import dotenv from "dotenv";
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
    backendUrl: process.env.BACKEND_URL || "http://localhost:3000",
    ilpUrl: process.env.ILP_URL || "http://localhost:3001",
    walletAddressUrl: process.env.WALLET_ADDRESS_URL || "",
    keyID: process.env.KEY_ID || "",
    privateKeyID: process.env.PRIVATE_KEY_ID || "",
  };

  return variables;
};
