import { client } from "./client";

export interface IWalletAddressResponse {
  id: string;
  publicName: string;
  assetCode: string;
  assetScale: number;
  authServer: string;
  resourceServer: string;
}

const validateWalletAddress = async (
  walletAddress: string
): Promise<IWalletAddressResponse | null> => {
  try {
    const response = await client.walletAddress.get({
      url: walletAddress,
    });

    return response as IWalletAddressResponse; // This should be the wallet address information
  } catch (error) {
    console.log("Wallet Address Validation Failed: ", error);
    return null;
  }
};

export { validateWalletAddress };

// const result = await validateWalletAddress(
//   "https://ilp.rafiki.money/test_accounts"
// );
// console.log(result);
