import {
  grantAccessRequest,
  Limits,
  incomingPaymentAccessRequest,
  quoteAccessRequest,
} from "../types/accounting";
import { GrantType } from "../types/validation";

export const buildQuoteAccessRequest = async (
  walletID: string,
  incomingPaymentUrl: string
): Promise<quoteAccessRequest> => {
  return {
    method: "ilp",
    walletAddress: walletID,
    receiver: incomingPaymentUrl,
  };
};

export const buildGrantAccessRequest = async (
  grantType: GrantType,
  walletId: string,
  paymentLimits?: Limits
): Promise<grantAccessRequest> => {
  switch (grantType) {
    case GrantType.IncomingPayment:
      return {
        type: "incoming-payment",
        actions: ["read", "create", "complete"],
      };
    case GrantType.OutgoingPayment:
      return {
        type: "outgoing-payment",
        actions: ["read", "create", "read-all", "list", "list-all"],
        identifier: walletId,
        limits: paymentLimits ? { ...paymentLimits } : undefined,
      };
    case GrantType.Quote:
      return {
        type: "quote",
        actions: ["create", "read", "read-all"],
      };
    default:
      throw new Error("Invalid grant type provided.");
  }
};

export const buildIncomingPaymentAccessRequest = async (
  walletId: string,
  walletAssetCode: string,
  walletAssetScale: number,
  expiryDate: number,
  value: string
): Promise<incomingPaymentAccessRequest> => {
  return {
    walletAddress: walletId,
    incomingAmount: {
      value: value,
      assetCode: walletAssetCode,
      assetScale: walletAssetScale,
    },
    expiresAt: new Date(expiryDate + 48 * 60 * 60 * 1000).toISOString(),
  };
};
