import {
  isPendingGrant,
  Grant,
  PendingGrant,
} from "@interledger/open-payments";
import { client } from "./client";
import { validateWalletAddress } from "./wallet";
import { randomUUID } from "crypto";

export enum GrantType {
  IncomingPayment = "incoming-payment",
  OutgoingPayment = "outgoing-payment",
  Quote = "quote",
}

type AccessRequest =
  | {
      type: "incoming-payment";
      actions: (
        | "read"
        | "create"
        | "complete"
        | "read-all"
        | "list"
        | "list-all"
      )[];
    }
  | {
      type: "outgoing-payment";
      actions: ("read" | "create" | "read-all" | "list" | "list-all")[];
      identifier: string;
    }
  | {
      type: "quote";
      actions: ("read" | "create" | "read-all")[];
    };

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
  grantType: GrantType
) => {
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
            uri: "<REDIRECT_URI>", // Replace with your redirect URI
            nonce: randomUUID(), // Replace with a secure nonce
          },
        },
      }
    );

    // Handle the pending state
    if (isPendingGrant(grant)) {
      const pendingGrant = grant as PendingGrant; // Cast to PendingGrant if needed
      console.log("Grant is pending. User interaction required.");
      console.log("Interact with the user at:", pendingGrant.interact.redirect); // Example field
      return {
        isPending: true,
        isRejected: false,
        isAccepted: false,
      };
    }

    // At this point, the grant must be of type `Grant`, so we can safely access `access_token`
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
