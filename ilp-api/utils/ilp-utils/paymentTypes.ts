import { client } from "./client";
import { IWalletAddressResponse } from "../types/wallet";
import { GrantType } from "../types/validation";
import { isPendingGrant } from "@interledger/open-payments";
import { randomUUID } from "crypto";
import { Grant, PendingGrant } from "@interledger/open-payments";
import { Limits, grantAccessRequest } from "../types/accounting";
import {
  buildGrantAccessRequest,
  buildIncomingPaymentAccessRequest,
  buildQuoteAccessRequest,
} from "./accessRequests";

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
