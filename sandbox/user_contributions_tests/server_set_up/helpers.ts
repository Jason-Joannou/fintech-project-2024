// Open Payments Helper Fucntions

// import env  from './env';
import {
  type WalletAddress,
  type AuthenticatedClient,
  type Grant,
  createAuthenticatedClient,
  type PendingGrant,
  isPendingGrant,
  type OutgoingPaymentWithSpentAmounts,
  isFinalizedGrant,
} from "@interledger/open-payments";

import { randomUUID } from "crypto";
import { type components } from "@interledger/open-payments/dist/openapi/generated/auth-server-types";


export async function getAuthenticatedClient() {
  let walletAddress = "https://ilp.rafiki.money/stokvel_app";

  if (walletAddress.startsWith("$")) {
    walletAddress = walletAddress.replace("$", "https://");
  }

  const client = await createAuthenticatedClient({
    walletAddressUrl: "https://ilp.rafiki.money/stokvel_app",//env.OPEN_PAYMENTS_CLIENT_ADDRESS,
    privateKey: "private.key",//env.OPEN_PAYMENTS_SECRET_KEY_PATH,
    keyId: "853aa509-9d78-4354-96d1-4236cbe1236e",//env.OPEN_PAYMENTS_KEY_ID,
    validateResponses: false, // Use this flag if you are having issues with the yaml files of the repo

  });
  return client;
}
//  function to set up an incoming payment (grant and actual payment place holder in the wallet)
export async function createStandardIncomingPayment(
    client: AuthenticatedClient,
    value: string,
    walletAddressDetails: WalletAddress,
  ) {
    // Request IP grant
    const grant = await client.grant.request(
      {
        url: walletAddressDetails.authServer,
      },
      {
        access_token: {
          access: [
            {
              type: "incoming-payment",
              actions: ["read", "create", "complete"],
            },
          ],
        },
      },
    );
  
    if (isPendingGrant(grant)) {
      throw new Error("Expected non-interactive grant");
    }
  
    // create incoming payment
    const incomingPayment = await client.incomingPayment.create(
      {
        url: new URL(walletAddressDetails.id).origin,
        accessToken: grant.access_token.value,
      },
      {
        walletAddress: walletAddressDetails.id,
        incomingAmount: {
          value: value,
          assetCode: walletAddressDetails.assetCode,
          assetScale: walletAddressDetails.assetScale,
        },
        expiresAt: new Date(Date.now() + 60_000 * 10).toISOString(),
      },
    );
  
    console.log("** Created Incoming Payment");
    console.log(incomingPayment);
  
    return incomingPayment;
  }

 //  function to set up an incoming payment on stokvel creation
 //  the creation of the stokvel and the first payout may be different therefore this method is also required
 //  this one is used specifically at stokvel creation
export async function createInitialIncomingPayment(
  client: AuthenticatedClient,
  value: string,
  walletAddressDetails: WalletAddress,
  stokvel_contributions_start_date: string
) {
  // Request IP grant
  const grant = await client.grant.request(
    {
      url: walletAddressDetails.authServer,
    },
    {
      access_token: {
        access: [
          {
            type: "incoming-payment",
            actions: ["read", "create", "complete"],
          },
        ],
      },
    },
  );

  if (isPendingGrant(grant)) {
    throw new Error("Expected non-interactive grant");
  }

  // create incoming payment
  const incomingPayment = await client.incomingPayment.create(
    {
      url: new URL(walletAddressDetails.id).origin,
      accessToken: grant.access_token.value,
    },
    {
      walletAddress: walletAddressDetails.id,
      incomingAmount: {
        value: value,
        assetCode: walletAddressDetails.assetCode,
        assetScale: walletAddressDetails.assetScale,
      },
      expiresAt: new Date(stokvel_contributions_start_date + 48 * 60 * 60 * 1000).toISOString(),
    },
  );

  console.log("** Income Payment");
  console.log(incomingPayment);

  return incomingPayment;
}


 //  function to set up an incoming payment on stokvel creation
 //  the creation of the stokvel and the first payout may be different therefore this method is also required
 //  this one is used specifically at stokvel creation
//  export async function createIncomingPayment(
//   client: AuthenticatedClient,
//   value: string,
//   walletAddressDetails: WalletAddress,
// ) {
//   // Request IP grant
//   const grant = await client.grant.request(
//     {
//       url: walletAddressDetails.authServer,
//     },
//     {
//       access_token: {
//         access: [
//           {
//             type: "incoming-payment",
//             actions: ["read", "create", "complete"],
//           },
//         ],
//       },
//     },
//   );

//   if (isPendingGrant(grant)) {
//     throw new Error("Expected non-interactive grant");
//   }

//   // create incoming payment
//   const incomingPayment = await client.incomingPayment.create(
//     {
//       url: new URL(walletAddressDetails.id).origin,
//       accessToken: grant.access_token.value,
//     },
//     {
//       walletAddress: walletAddressDetails.id,
//       incomingAmount: {
//         value: value,
//         assetCode: walletAddressDetails.assetCode,
//         assetScale: walletAddressDetails.assetScale,
//       },
//       expiresAt: new Date(Date.now() + 60_000 * 10).toISOString(),
//     },
//   );

//   console.log("** Income Payment");
//   console.log(incomingPayment);

//   return incomingPayment;
// }


export async function createQuote(
  client: AuthenticatedClient,
  incomingPaymentUrl: string,
  walletAddressDetails: WalletAddress,
) {
  // Request quote grant
  const quote_grant = await client.grant.request(
    {
      url: walletAddressDetails.authServer,
    },
    {
      access_token: {
        access: [
          {
            type: "quote",
            actions: ["create", "read", "read-all"],
          },
        ],
      },
    },
  );

  if (isPendingGrant(quote_grant)) {
    throw new Error("Expected non-interactive grant");
  }

  const quote = await client.quote.create(
    {
      url: new URL(walletAddressDetails.id).origin,
      accessToken: quote_grant.access_token.value,
    },
    {
      method: "ilp",
      walletAddress: walletAddressDetails.id,
      receiver: incomingPaymentUrl,
    },
  );

  console.log("** quote");
  console.log(quote);
  console.log('quote id for this payment: ', quote.id) // save to the database
  console.log('quote grant access token: ', quote_grant.access_token.value) //save to the database - to be used to retrieve quotes
  return quote;//what can we do now that we have the quote grant instead?
}

export async function getWalletAddressInfo(
  client: AuthenticatedClient,
  walletAddress: string,
): Promise<[string, WalletAddress]> {
  if (walletAddress.startsWith("$"))
    walletAddress = walletAddress.replace("$", "https://");

  const walletAddressDetails = await client.walletAddress.get({
    url: walletAddress,
  });

  return [walletAddress, walletAddressDetails];
}

// create the recurring grant
// will need to be done when actually joining a stokvel
export async function getOutgoingPaymentAuthorization(
  client: AuthenticatedClient,
  walletAddressDetails: WalletAddress,
  stokvel_contributions_start_date: string,
  payment_periods: number,
  payment_period_length: string, //this needs to come in as either (Y, M, D, T30S),
  quote_id: string,
  // quote_access_token: string

): Promise<PendingGrant> {
  const dateNow = new Date().toISOString();

  // retrieve the quote we need to work with: 

  // const quote = await client.quote.get({
  //   url: quote_id,
  //   accessToken: quote_access_token,
  // });

  // console.log(quote.id)
  // console.log quote.accessToken


  // const debitAmount = quote.debitAmount; // this needs to be a number in relation to the stokvel
  // const receiveAmount = quote.receiveAmount; // make this infinitely large?

  const receiveAmount =  { value: '100', assetCode: 'ZAR', assetScale: 2 };
  const debitAmount =  { value: '102', assetCode: 'ZAR', assetScale: 2 };

  debitAmount.value = (parseFloat(debitAmount.value)*payment_periods).toString(); // expect to payout all of the periods at some point
  receiveAmount.value = (parseFloat(receiveAmount.value)*payment_periods).toString();

  console.log(debitAmount, '\n', receiveAmount)



  // Request OP grant
  const pending_recurring_grant = await client.grant.request(
    {
      url: walletAddressDetails.authServer,
    },
    {
      access_token: {
        access: [
          {
            identifier: walletAddressDetails.id,
            type: "outgoing-payment",
            actions: ["list", "list-all", "read", "read-all", "create"],
            limits: {
              debitAmount: debitAmount,
              receiveAmount: receiveAmount,
              interval: "R12/2024-10-05T21:54:22Z/P1M"//`R${payment_periods}/${dateNow}/PT30S` //will need to change this to start date of the stokvel
            },
          },
        ],
      },
      interact: {
        start: ["redirect"]
        // finish: {
        //   method: "redirect",
        //   uri: input.redirectUrl,
        //   nonce: randomUUID(),
        // },
      },
    }
  );

  if (!isPendingGrant(pending_recurring_grant)) {
    throw new Error("Expected interactive grant");
  }

  // console.log(pending_recurring_grant.continue.)
  console.log('GRANT STUFFS - GRANT CREATIONS')
  console.log(pending_recurring_grant.continue.uri) // save this to the database
  console.log(pending_recurring_grant.continue.access_token.value)  // save this to the database as the current quote (until a payment is made, this will be the token to use)
  console.log(pending_recurring_grant.interact.redirect) //save this to the database as well this is where the user is going to go to authorize the grant

  console.log('printing the grant:')
  console.log(pending_recurring_grant)

  return pending_recurring_grant;
}

export async function createInitialOutgoingPayment(
  client: AuthenticatedClient,
  // input: OPCreateSchema,
  quote_id: string,
  // quote_access_token: string,
  continueUri: string,
  continueAccessToken: string,
  sender_wallet_address: string,
) {
  let walletAddress = sender_wallet_address
  if (walletAddress.startsWith("$"))
    walletAddress = walletAddress.replace("$", "https://");

  const walletAddressDetails = await client.walletAddress.get({
      url: walletAddress,
    });

  const finalizedOutgoingPaymentGrant = (await client.grant.continue({ //check which key/token pair should be used here
    accessToken: continueAccessToken,
    url: continueUri
  }
  // {
  //   interact_ref: interactRef
  // }
  )) as Grant;

  console.log('Grant details')
  console.log(finalizedOutgoingPaymentGrant.continue)
  console.log(finalizedOutgoingPaymentGrant.continue.access_token)
  console.log('the last thing I can thinkk of: ')
  // console.log(finalizedOutgoingPaymentGrant.access_token.value)

  if (!isFinalizedGrant(finalizedOutgoingPaymentGrant)) {
    throw new Error("Expected finalized grant. The grant might not be accepted or might be already used.");
  }

    // const quote = await client.quote.get({
    //   url: quote_id,
    //   accessToken: quote_access_token
    // });

    // console.log('got the quote: quote details \n', quote)

    console.log('wallet address stuffs',walletAddressDetails.id)

  const outgoingPayment = await client.outgoingPayment.create(
    {
      url: new URL(walletAddressDetails.id).origin,
      accessToken: finalizedOutgoingPaymentGrant.access_token.value, //OUTGOING_PAYMENT_ACCESS_TOKEN,-- this is the one we need to save in the DB? does the token
    },
    {
      walletAddress: walletAddress,
      quoteId: quote_id, //QUOTE_URL taken from the input parameters,
    },
  );

  console.log("** Outgoing Payment Grant");
  console.log(finalizedOutgoingPaymentGrant.access_token);

  console.log('INITIAL PAYMENT PARAMETERS - SAVE TO DB')

  console.log(finalizedOutgoingPaymentGrant.access_token.value) //store in DB - use in next payment, then overrite with new
  console.log(finalizedOutgoingPaymentGrant.access_token.manage) //store in DB - use in next payment, then overrite with new


  return outgoingPayment;


}


export async function processRecurringPayments(
  client: AuthenticatedClient,
  sender_wallet_address: string,
  receiving_wallet_address: string,
  quoteId: string,
  manageUrl: string,
  previousToken: string,

) {
  // rotate the token
  const token = await client.token.rotate({
    url: manageUrl,
    accessToken: previousToken,
  });

  console.log(token.access_token.manage) // update this in the DB
  console.log(token.access_token.value) //update this in the DB

  if (!token.access_token) {
    console.error("** Failed to rotate token.");
  }

  console.log("** Rotated Token ");
  console.log(token.access_token);

  const tokenAccessDetails = token.access_token.access as {
    type: "outgoing-payment";
    actions: ("create" | "read" | "read-all" | "list" | "list-all")[];
    identifier: string;
    limits?: components["schemas"]["limits-outgoing"];
  }[];

  const receiveAmount = tokenAccessDetails[0]?.limits?.receiveAmount?.value;

  const [receiverWalletAddress, receiverWalletAddressDetails] =
    await getWalletAddressInfo(client, receiving_wallet_address);

  const [senderWalletAddress, senderWalletAddressDetails] =
    await getWalletAddressInfo(client, tokenAccessDetails[0]?.identifier ?? "");

  // create incoming payment
  const incomingPayment = await createStandardIncomingPayment(
    client,
    receiveAmount!,
    receiverWalletAddressDetails,
  );

  // create qoute
  const quote = await createQuote(
    client,
    incomingPayment.id,
    senderWalletAddressDetails,
  );

  // create outgoing payment
  try {
    const outgoingPayment = await client.outgoingPayment.create(
      {
        url: new URL(senderWalletAddress).origin,
        accessToken: token.access_token.value, //OUTGOING_PAYMENT_ACCESS_TOKEN -- using the new token
      },
      {
        walletAddress: senderWalletAddress,
        quoteId: quote.id, //QUOTE_URL,
      },
    );

    //update the stuffs (token details) in the database now

    return outgoingPayment;
  } catch (error) {
    console.log(error);
    return {
      id: "",
      walletAddress: senderWalletAddress,
      quoteId: quote.id,
      failed: true,
      receiver: "",
      receiveAmount: tokenAccessDetails[0]?.limits?.receiveAmount,
      debitAmount: tokenAccessDetails[0]?.limits?.debitAmount,
      sentAmount: tokenAccessDetails[0]?.limits?.debitAmount,
      createdAt: "",
      updatedAt: "",
    } as OutgoingPaymentWithSpentAmounts;
  }
}