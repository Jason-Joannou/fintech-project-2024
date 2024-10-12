import { createAuthenticatedClient } from "@interledger/open-payments";
import { getEnviromentVariables } from "../../enviroment/index";

const { walletAddressUrl, keyID, privateKeyID } = getEnviromentVariables();

export const client = await createAuthenticatedClient({
  walletAddressUrl,
  keyId: keyID,
  privateKey: privateKeyID,
  validateResponses: false,
});
