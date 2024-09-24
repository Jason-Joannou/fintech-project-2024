import { createAuthenticatedClient } from "@interledger/open-payments";
import { getEnviromentVariables } from "../../enviroment/index";

const { walletAddressUrl, keyID, privateKeyID } = getEnviromentVariables();

console.log({ walletAddressUrl, keyID, privateKeyID });

export const client = await createAuthenticatedClient({
  walletAddressUrl,
  keyId: keyID,
  privateKey: privateKeyID,
  validateResponses: false,
});
