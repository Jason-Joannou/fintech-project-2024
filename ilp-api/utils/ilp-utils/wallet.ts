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
): Promise<IWalletAddressResponse> => {
  try {
    if (walletAddress.startsWith("$")) {
      walletAddress = walletAddress.replace("$", "https://");
    }
    const response = await client.walletAddress.get({
      url: walletAddress,
    });
    return response as IWalletAddressResponse; // This should be the wallet address information
  } catch (error: unknown) {
    if (error instanceof OpenPaymentsClientError) {
      const invalidWalletError: InvalidWalletResponse = {
        ...error,
        status: error.status || 500,
        description: error.description || "Unknown error occurred",
      };
      // Throw the error so it can be caught by the calling function
      throw invalidWalletError;
    }

    console.error("Unexpected error type:", error);
    throw new Error("An unexpected error occurred during wallet validation.");
  }
};

export { validateWalletAddress };
