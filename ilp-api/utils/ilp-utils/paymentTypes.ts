import { client } from "./client";
import { IWalletAddressResponse } from "../types/wallet";
import { GrantType } from "../types/validation";
import { AccessRequest, Limits } from "../types/accounting";
import { isPendingGrant } from "@interledger/open-payments";
import { randomUUID } from "crypto";

const buildAccessRequest = (
  grantType: GrantType,
  walletId: string,
  paymentLimits?: Limits
): AccessRequest => {
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
        actions: ["read"],
      };
    default:
      throw new Error("Invalid grant type provided.");
  }
};

export const createGrant = async (
  walletAddress: IWalletAddressResponse,
  grantType: GrantType,
  withInteraction: boolean,
  paymentLimits?: Limits
) => {
  try {
    let accessRequest: AccessRequest;

    if (paymentLimits) {
      accessRequest = buildAccessRequest(
        grantType,
        walletAddress.id,
        paymentLimits
      );
    } else {
      accessRequest = buildAccessRequest(grantType, walletAddress.id);
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
