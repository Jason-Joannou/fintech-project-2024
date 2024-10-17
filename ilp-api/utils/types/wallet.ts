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
