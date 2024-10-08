import { client } from "./client";
import { OpenPaymentsClientError } from "@interledger/open-payments";

export interface IWalletAddressResponse {
  id: string;
  publicName: string;
  assetCode: string;
  assetScale: number;
  authServer: string;
  resourceServer: string;
}

export interface InvalidWalletResponse extends OpenPaymentsClientError {
  status: number;
  description: string;
}

const validateWalletAddress = async (
  walletAddress: string
): Promise<IWalletAddressResponse | InvalidWalletResponse | null> => {
  try {
    const response = await client.walletAddress.get({
      url: walletAddress,
    });

    return response as IWalletAddressResponse; // This should be the wallet address information
  } catch (error: unknown) {
    if (error instanceof OpenPaymentsClientError) {
      return {
        ...error,
        status: error.status || 500,
        description: error.description || "Unknown error occurred",
      } as InvalidWalletResponse;
    }

    console.error("Unexpected error type:", error);
    return null;
  }
};

export { validateWalletAddress };

const result = await validateWalletAddress(
  "https://ilp.rafiki.money/test_account"
);
console.log(result);
