import {
  isPendingGrant,
  Grant,
  PendingGrant,
} from "@interledger/open-payments";
import { client } from "./client";
import { validateWalletAddress } from "./wallet";
import { randomUUID } from "crypto";
import {
  GrantType,
  AccessRequest,
  GrantStatusResult,
} from "../types/validation";

const buildAccessRequest = (
  grantType: GrantType,
  walletId: string
): AccessRequest => {
  switch (grantType) {
    case GrantType.IncomingPayment:
      return {
        type: "incoming-payment",
        actions: ["read"],
      };
    case GrantType.OutgoingPayment:
      return {
        type: "outgoing-payment",
        actions: ["read"],
        identifier: walletId,
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

const checkGrantStatus = async (
  walletAddress: string,
  grantType: GrantType,
  interactionUri?: string // New parameter to track a specific grant by URI
): Promise<GrantStatusResult> => {
  try {
    const validatedWalletAddress = await validateWalletAddress(walletAddress);
    const accessRequest = buildAccessRequest(
      grantType,
      validatedWalletAddress.id
    );

    const grant = await client.grant.request(
      {
        url: validatedWalletAddress.authServer,
      },
      {
        access_token: {
          access: [accessRequest],
        },
        interact: {
          start: ["redirect"],
          finish: {
            method: "redirect",
            uri: "<REDIRECT_URI>", // Replace with our redirect URI
            nonce: randomUUID(),
          },
        },
      }
    );

    // Handle the pending state
    if (isPendingGrant(grant)) {
      const pendingGrant = grant as PendingGrant;

      // Check if the pending grant's continue URI matches the provided interaction URI
      if (interactionUri && pendingGrant.continue.uri === interactionUri) {
        console.log(`Grant with continue URI ${interactionUri} is pending.`);
      } else {
        console.log("Grant is pending but no specific URI was matched.");
      }

      console.log("Interact with the user at:", pendingGrant.interact.redirect);
      return {
        isPending: true,
        isRejected: false,
        isAccepted: false,
        continueUri: pendingGrant.continue.uri, // Returning continue URI for reference
      };
    }

    // If the grant is not pending, we check if it's accepted or rejected
    const isAccepted = !!(grant as Grant).access_token;
    return {
      isPending: false,
      isRejected: !isAccepted,
      isAccepted: isAccepted,
    };
  } catch (error) {
    console.error("Error checking if grant is active:", error);
    throw error;
  }
};

export { checkGrantStatus };
