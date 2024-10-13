import { client } from "./client";
import { IWalletAddressResponse } from "../types/wallet";
import { GrantType } from "../types/validation";
import {
  grantAccessRequest,
  Limits,
  incomingPaymentAccessRequest,
  quoteAccessRequest,
} from "../types/accounting";
import { isPendingGrant } from "@interledger/open-payments";
import { randomUUID } from "crypto";
import { Grant, PendingGrant } from "@interledger/open-payments";

const buildQuoteAccessRequest = async (
  walletID: string,
  incomingPaymentUrl: string
): Promise<quoteAccessRequest> => {
  return {
    method: "ilp",
    walletAddress: walletID,
    receiver: incomingPaymentUrl,
  };
};

const buildGrantAccessRequest = async (
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

const buildIncomingPaymentAccessRequest = async (
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

export const createGrant = async (
  walletAddress: IWalletAddressResponse,
  grantType: GrantType,
  withInteraction: boolean,
  paymentLimits?: Limits
): Promise<Grant | PendingGrant> => {
  try {
    let accessRequest: grantAccessRequest;

    if (paymentLimits) {
      accessRequest = await buildGrantAccessRequest(
        grantType,
        walletAddress.id,
        paymentLimits
      );
    } else {
      accessRequest = await buildGrantAccessRequest(
        grantType,
        walletAddress.id
      );
    }

    const interact = withInteraction
      ? {
          interact: {
            start: ["redirect"],
            finish: {
              method: "redirect",
              uri: "<REDIRECT_URI>",
              nonce: randomUUID(),
            },
          },
        }
      : {};

    const grantPayload = {
      access_token: {
        access: [accessRequest],
        ...interact,
      },
    };

    const grant = await client.grant.request(
      {
        url: walletAddress.authServer,
      },
      grantPayload
    );

    return grant;
  } catch (error) {
    // Log or handle the error accordingly
    console.error("Error creating grant:", error);
    throw new Error("Failed to create grant.");
  }
};

export const createIncomingPayment = async (
  walletAddress: IWalletAddressResponse,
  value: string,
  grant: Grant,
  expiresAt: string
) => {
  try {
    const stokvel_contributions_start_date_converted = Date.parse(expiresAt);
    const incomingPaymentPayload = await buildIncomingPaymentAccessRequest(
      walletAddress.id,
      walletAddress.assetCode,
      walletAddress.assetScale,
      stokvel_contributions_start_date_converted,
      value
    );

    const incomingPayment = await client.incomingPayment.create(
      {
        url: new URL(walletAddress.id).origin,
        accessToken: grant.access_token.value,
      },
      incomingPaymentPayload
    );

    return incomingPayment;
  } catch (error) {
    // Log or handle the error accordingly
    console.error("Error creating IncomingPayment:", error);
    throw new Error("Failed to create IncomingPayment.");
  }
};

export const createQuote = async (
  walletAddress: IWalletAddressResponse,
  incomingPaymentUrl: string
) => {
  try {
    const grant_quote = (await createGrant(
      walletAddress,
      GrantType.Quote,
      false
    )) as Grant;
    const quotePayload = await buildQuoteAccessRequest(
      walletAddress.id,
      incomingPaymentUrl
    );
    const quote = await client.quote.create(
      {
        url: new URL(walletAddress.id).origin,
        accessToken: grant_quote.access_token.value,
      },
      quotePayload
    );
    return quote;
  } catch (error) {
    // Log or handle the error accordingly
    console.error("Error creating quote:", error);
    throw new Error("Failed to create quote.");
  }
};
