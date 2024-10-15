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
import {
  recurringGrantType,
  outgoingPaymentType,
  interactType,
} from "../types/validation";
import { validateWalletAddress } from "./wallet";

export const createGrant = async (
  walletAddress: IWalletAddressResponse,
  grantType: GrantType,
  withInteraction: boolean,
  dynamicEndpoint: string = "user",
  paymentLimits?: Limits,
  userId?: string,
  stokvelId?: string
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
      ? ({
          interact: {
            start: ["redirect"],
            finish: {
              method: "redirect",
              uri: `http://localhost:5000/stokvel/create_stokvel/${dynamicEndpoint}_interactive_grant_response?user_id=${userId}&stokvel_id=${stokvelId}`,
              nonce: randomUUID(),
            },
          },
        } as interactType)
      : {};

    const grantPayload = {
      access_token: {
        access: [accessRequest],
      },
      ...interact,
    };

    console.log(grantPayload);

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

export const createRecurringGrant = async (
  authParameters: recurringGrantType
): Promise<PendingGrant> => {
  try {
    const stokvel_contributions_start_date_converted = new Date(
      authParameters.stokvelContributionStartDate
    ).toISOString(); // Example date

    const interval = `R${authParameters.payment_periods}/${stokvel_contributions_start_date_converted}/P${authParameters.number_of_periods}${authParameters.payment_period_length}`;

    const paymentLimits = {
      debitAmount: authParameters.debitAmount,
      receiveAmount: authParameters.receiveAmount,
      interval: interval,
    };

    const pending_recurring_grant = await createGrant(
      authParameters.senderWalletAddress,
      GrantType.OutgoingPayment,
      true,
      "user",
      paymentLimits,
      authParameters.user_id,
      authParameters.stokvel_id
    );

    return pending_recurring_grant as PendingGrant;
  } catch (error) {
    console.error(error);
    throw new Error("An unexpected error occurred during authorization.");
  }
};

export const createInitialOutgoingPayment = async (
  authParameters: outgoingPaymentType
) => {
  try {
    const senderWalletAddress = await validateWalletAddress(
      authParameters.senderWalletAddress
    );

    const outgoingPaymentGrant = (await client.grant.continue(
      {
        accessToken: authParameters.continueAccessToken,
        url: authParameters.continueUri,
      },
      {
        interact_ref: authParameters?.interactRef,
      }
    )) as Grant;

    const outgoingPayment = await client.outgoingPayment.create(
      {
        url: new URL(senderWalletAddress.id).origin,
        accessToken: outgoingPaymentGrant.access_token.value,
      },
      {
        walletAddress: senderWalletAddress.id,
        quoteId: authParameters.quote_id,
      }
    );

    return {
      payment: outgoingPayment,
      token: outgoingPaymentGrant.access_token.value,
      manageurl: outgoingPaymentGrant.access_token.manage,
    };
  } catch (error) {
    console.error(error);
    throw new Error("An unexpected error occurred during authorization.");
  }
};

export const createOutgoingPayment = async (
  authParameters: outgoingPaymentType
) => {
  try {
    const senderWalletAddress = await validateWalletAddress(
      authParameters.senderWalletAddress
    );

    const outgoingPayment = await client.outgoingPayment.create(
      {
        url: new URL(senderWalletAddress.id).origin,
        accessToken: authParameters?.tokenValue as string,
      },
      {
        walletAddress: senderWalletAddress.id,
        quoteId: authParameters.quote_id,
      }
    );

    return {
      payment: outgoingPayment,
    };
  } catch (error) {
    console.error(error);
    throw new Error("An unexpected error occurred during authorization.");
  }
};

export const createRecurringGrantWithStokvelLimits = async (
  authParameters: recurringGrantType
): Promise<PendingGrant> => {
  try {
    const stokvel_contributions_start_date_converted = new Date(
      authParameters.stokvelContributionStartDate
    ).toISOString(); // Example date

    authParameters.debitAmount.value = "1000000000";
    authParameters.receiveAmount.value = "1000000000";

    const interval = `R${authParameters.payment_periods}/${stokvel_contributions_start_date_converted}/P${authParameters.number_of_periods}${authParameters.payment_period_length}`;

    const paymentLimits = {
      debitAmount: authParameters.debitAmount,
      receiveAmount: authParameters.receiveAmount,
      interval: interval,
    };

    const pending_recurring_grant = await createGrant(
      authParameters.senderWalletAddress,
      GrantType.OutgoingPayment,
      true,
      "stokvel",
      paymentLimits,
      authParameters.user_id,
      authParameters.stokvel_id
    );

    return pending_recurring_grant as PendingGrant;
  } catch (error) {
    console.error(error);
    throw new Error("An unexpected error occurred during authorization.");
  }
};
