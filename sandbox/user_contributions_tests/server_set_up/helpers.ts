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
import { access } from "fs";
import { string } from "zod";


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
  walletAddressDetails: WalletAddress, //RECEIVER ADDRESS!!!
  stokvel_contributions_start_date: string
) {
  // Request IP grant
  // const dateNow = new Date().toISOString();
  // console.log(dateNow)
  const stokvel_contributions_start_date_converted = Date.parse(stokvel_contributions_start_date);  // Example date

  console.log("EXPIRATION DATE: \n", stokvel_contributions_start_date_converted)

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
      expiresAt: new Date(stokvel_contributions_start_date_converted + 48 * 60 * 60 * 1000).toISOString(),
    },
  );



  console.log("** Income Payment");
  console.log(incomingPayment);

  return incomingPayment;
}



export async function createQuote(
  client: AuthenticatedClient,
  incomingPaymentUrl: string,
  walletAddressDetails: WalletAddress, //senders wallet address
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

interface Amount {
  value: string;       // The value of the amount (in string to avoid floating point errors)
  assetCode: string;   // Currency code (e.g., USD, ZAR)
  assetScale: number;  // Scale of the currency (e.g., 2 for cents)
}


// create the recurring grant
// will need to be done when actually joining a stokvel
export async function getOutgoingPaymentAuthorization(
  client: AuthenticatedClient,
  walletAddressDetails: WalletAddress,
  stokvel_contributions_start_date: string,
  payment_periods: number,
  payment_period_length: string, //this needs to come in as either (Y, M, D, T30S),
  length_between_periods:string,
  quote_id: string,
  debitAmount:Amount,
  receiveAmount:Amount,
  user_id: number,
  stokvel_id:number
): Promise<PendingGrant> {
  const dateNow = new Date().toISOString();
  console.log(dateNow)
  const stokvel_contributions_start_date_converted = new Date(stokvel_contributions_start_date).toISOString();  // Example date

  console.log(stokvel_contributions_start_date)
 
  console.log(debitAmount, '\n', receiveAmount)


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
              interval: `R${payment_periods}/${stokvel_contributions_start_date_converted}/P${length_between_periods}${payment_period_length}` //will need to change this to start date of the stokvel
            },
          },
        ],
      },
      interact: {
        start: ["redirect"],
        finish: {
          method: "redirect",
          uri: `http://localhost:5000/stokvel/create_stokvel/user_interactive_grant_response?user_id=${user_id}&stokvel_id=${stokvel_id}`,
          nonce: randomUUID(),
        },
      },
    }
  );

  if (!isPendingGrant(pending_recurring_grant)) {
    throw new Error("Expected interactive grant");
  }

  // console.log(pending_recurring_grant.continue.)
  console.log('GRANT STUFFS - GRANT CREATIONS')

  console.log('PENDING GRANT WITH REDIRECT: ', pending_recurring_grant)


  console.log(pending_recurring_grant.continue.uri) // save this to the database
  console.log(pending_recurring_grant.continue.access_token.value)  // save this to the database as the current quote (until a payment is made, this will be the token to use)
  console.log(pending_recurring_grant.interact.redirect) //save this to the database as well this is where the user is going to go to authorize the grant

  console.log('printing the grant:')
  console.log(pending_recurring_grant)

  return pending_recurring_grant;
}

export async function getOutgoingPaymentAuthorization_AdhocPayment(
  client: AuthenticatedClient,
  walletAddressDetails: WalletAddress,
  debitAmount:Amount,
  receiveAmount:Amount,
  user_id: number,
  stokvel_id:number,
  quote_id: string,
): Promise<PendingGrant> {
  const dateNow = new Date().toISOString();
  console.log(dateNow)
  console.log(debitAmount, '\n', receiveAmount)

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
            },
          },
        ],
      },
      interact: {
        start: ["redirect"],
        finish: {
          method: "redirect",
          uri: `http://localhost:5000/stokvel/adhoc_payment_grant_accept?user_id=${user_id}&stokvel_id=${stokvel_id}&quote_id=${quote_id}`,
          nonce: randomUUID(),
        },
      },
    }
  );

  if (!isPendingGrant(pending_recurring_grant)) {
    throw new Error("Expected interactive grant");
  }

  // console.log(pending_recurring_grant.continue.)
  console.log('GRANT STUFFS - GRANT CREATIONS')

  console.log('PENDING GRANT WITH REDIRECT: ', pending_recurring_grant)


  console.log(pending_recurring_grant.continue.uri) // save this to the database
  console.log(pending_recurring_grant.continue.access_token.value)  // save this to the database as the current quote (until a payment is made, this will be the token to use)
  console.log(pending_recurring_grant.interact.redirect) //save this to the database as well this is where the user is going to go to authorize the grant

  console.log('printing the grant:')
  console.log(pending_recurring_grant)

  return pending_recurring_grant;
}


export async function createInitialOutgoingPayment(
  client: AuthenticatedClient,
  quote_id: string,
  continueUri: string,
  continueAccessToken: string,
  sender_wallet_address: string,
  interact_ref:string
) {
  let walletAddress = sender_wallet_address
  if (walletAddress.startsWith("$"))
    walletAddress = walletAddress.replace("$", "https://");

  const walletAddressDetails = await client.walletAddress.get({
      url: walletAddress,
    });

    console.log('ABOUT TO CONTINUE THE GRANT')

  const finalizedOutgoingPaymentGrant = (await client.grant.continue({ //check which key/token pair should be used here
    accessToken: continueAccessToken,
    url: continueUri
  },
  {
    interact_ref:interact_ref
  }

  )) as Grant;

  console.log('GRANT CONTINUED')


  console.log('Grant details')
  console.log(finalizedOutgoingPaymentGrant.continue)
  console.log(finalizedOutgoingPaymentGrant.continue.access_token)
  console.log('the last thing I can thinkk of: ')

  if (!isFinalizedGrant(finalizedOutgoingPaymentGrant)) {
    throw new Error("Expected finalized grant. The grant might not be accepted or might be already used.");
  }

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

  console.log('INITIAL PAYMENT PARAMETERS - SAVE TO DB - USE IN THE RECURRING PAYMENTS!!!!!')
  console.log(finalizedOutgoingPaymentGrant.access_token.value) //store in DB - use in next payment, then overrite with new
  console.log(finalizedOutgoingPaymentGrant.access_token.manage) //store in DB - use in next payment, then overrite with new


  return {payment: outgoingPayment, token: finalizedOutgoingPaymentGrant.access_token.value, manageurl: finalizedOutgoingPaymentGrant.access_token.manage};


}


export async function processRecurringPayments(
  client: AuthenticatedClient,
  sender_wallet_address: string,
  receiving_wallet_address: string,
  // quoteId: string, // the previous quote
  manageUrl: string, //manage url from the 
  previousToken: string,

) {
  // rotate the token
  const token = await client.token.rotate({
    url: manageUrl,
    accessToken: previousToken,
  });

  console.log('ROTATED THE TOKEN')

  console.log(token.access_token.manage) // update this in the DB AND USE IN THE NEXT PAYMNET CYCLE TO ROTATE THE TOKEN
  console.log(token.access_token.value) //update this in the DB AND USE IN THE NEXT PAYMNET CYCLE TO ROTATE THE TOKEN

  const manageurl = token.access_token.manage;
  const used_token = token.access_token.value;

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

    return {outgoingPayment: outgoingPayment, manageurl: manageurl, token: used_token};
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

export async function getOutgoingPaymentAuthorization_HugeLimit_StokvelPayout(
  client: AuthenticatedClient,
  walletAddressDetails: WalletAddress,
  stokvel_contributions_start_date: string,
  payment_periods: number,
  payment_period_length: string, //this needs to come in as either (Y, M, D, T30S),
  quote_id: string,
  debitAmount:Amount,
  receiveAmount:Amount,
  number_of_periods:string,
  user_id:number,
  stokvel_id:number
): Promise<PendingGrant> {
  const dateNow = new Date().toISOString();
  console.log(dateNow)
  const stokvel_contributions_start_date_converted = new Date(stokvel_contributions_start_date).toISOString();  // Example date

  console.log(stokvel_contributions_start_date)
 
  console.log(debitAmount, '\n', receiveAmount)

  debitAmount.value = "1000000"
  receiveAmount.value = "1000000"



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
              interval: `R${payment_periods}/${stokvel_contributions_start_date_converted}/P${number_of_periods}${payment_period_length}` //will need to change this to start date of the stokvel
            },
          },
        ],
      },
      interact: {
        start: ["redirect"],
        finish: {
          method: "redirect",
          uri: `http://localhost:5000/stokvel/create_stokvel/stokvel_interactive_grant_response?user_id=${user_id}&stokvel_id=${stokvel_id}`,
          nonce: randomUUID(),
        },
          // finish: {
          // method: "redirect",
          // uri: "http://localhost:5000/stokvel/create_stokvel/success_contribution_grant_confirmed",
          // nonce: randomUUID(),
        //}
        // finish: {
        //   method: "redirect",
        //   uri: input.redirectUrl,
        //   nonce: randomUUID(),
        // },
      },
    }
  );

  console.log('PENDING GRANT WITH REDIRECT: ', pending_recurring_grant)

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

export async function getOutgoingPaymentAuthorization_VariableContribution(
  client: AuthenticatedClient,
  walletAddressDetails: WalletAddress,
  stokvel_contributions_start_date: string,
  payment_periods: number,
  payment_period_length: string, //this needs to come in as either (Y, M, D, T30S),
  quote_id: string,
  debitAmount:Amount,
  receiveAmount:Amount,
  number_of_periods:string,
  user_id:number,
  stokvel_id:number,
  max_debit:string,
  max_receive:string,
): Promise<PendingGrant> {
  const dateNow = new Date().toISOString();
  console.log(dateNow)
  const stokvel_contributions_start_date_converted = new Date(stokvel_contributions_start_date).toISOString();  // Example date

  console.log(stokvel_contributions_start_date)
 
  console.log(debitAmount, '\n', receiveAmount)

  debitAmount.value = max_debit
  receiveAmount.value = max_receive



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
              interval: `R${payment_periods}/${stokvel_contributions_start_date_converted}/P${number_of_periods}${payment_period_length}` //will need to change this to start date of the stokvel
            },
          },
        ],
      },
      interact: {
        start: ["redirect"],
        finish: {
          method: "redirect",
          uri: `http://localhost:5000/stokvel/create_stokvel/stokvel_interactive_grant_response?user_id=${user_id}&stokvel_id=${stokvel_id}`,
          nonce: randomUUID(),
        },
      },
    }
  );

  console.log('PENDING GRANT WITH REDIRECT: ', pending_recurring_grant)

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




export async function processInterestAddedRecurringPayments(
  client: AuthenticatedClient,
  sender_wallet_address: string,
  receiving_wallet_address: string,
  // quoteId: string, // the previous quote
  manageUrl: string, //manage url from the 
  previousToken: string,
  payout_value: string

) {
  // rotate the token
  const token = await client.token.rotate({
    url: manageUrl,
    accessToken: previousToken,
  });

  console.log('ROTATED THE TOKEN')

  console.log(token.access_token.manage) // update this in the DB AND USE IN THE NEXT PAYMNET CYCLE TO ROTATE THE TOKEN
  console.log(token.access_token.value) //update this in the DB AND USE IN THE NEXT PAYMNET CYCLE TO ROTATE THE TOKEN

  const manageurl = token.access_token.manage;
  const used_token = token.access_token.value

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


  let receiveAmount = tokenAccessDetails[0]?.limits?.receiveAmount?.value;
  if (payout_value != null){
    receiveAmount = payout_value;
  }
  
  const [receiverWalletAddress, receiverWalletAddressDetails] =
    await getWalletAddressInfo(client, receiving_wallet_address);

  const [senderWalletAddress, senderWalletAddressDetails] =
    await getWalletAddressInfo(client, sender_wallet_address);

  // create incoming payment
  const incomingPayment = await createStandardIncomingPayment(
    client,
    receiveAmount!,
    receiverWalletAddressDetails,
  );

  console.log('recurring payment with interest: \n', incomingPayment)

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

    return {outgoingPayment: outgoingPayment, manageurl: manageurl, token: used_token};
  } catch (error) {
    console.log(error);
    return {
      id: "",
      walletAddress: senderWalletAddress,
      quoteId: quote.id,
      failed: true,
      receiver: "",
      // receiveAmount: tokenAccessDetails[0]?.limits?.receiveAmount,
      // debitAmount: tokenAccessDetails[0]?.limits?.debitAmount,
      // sentAmount: tokenAccessDetails[0]?.limits?.debitAmount,
      createdAt: "",
      updatedAt: "",
    } as OutgoingPaymentWithSpentAmounts;
  }
}


export async function processVariableRecurringPayments(
  client: AuthenticatedClient,
  sender_wallet_address: string,
  receiving_wallet_address: string,
  // quoteId: string, // the previous quote
  manageUrl: string, //manage url from the 
  previousToken: string,
  contriubtion_amount: string

) {
  // rotate the token
  const token = await client.token.rotate({
    url: manageUrl,
    accessToken: previousToken,
  });

  console.log('ROTATED THE TOKEN')

  console.log(token.access_token.manage) // update this in the DB AND USE IN THE NEXT PAYMNET CYCLE TO ROTATE THE TOKEN
  console.log(token.access_token.value) //update this in the DB AND USE IN THE NEXT PAYMNET CYCLE TO ROTATE THE TOKEN

  const manageurl = token.access_token.manage;
  const used_token = token.access_token.value

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


  let receiveAmount = tokenAccessDetails[0]?.limits?.receiveAmount?.value;
  if (contriubtion_amount != null){
    receiveAmount = contriubtion_amount;
  }
  
  const [receiverWalletAddress, receiverWalletAddressDetails] =
    await getWalletAddressInfo(client, receiving_wallet_address);

  const [senderWalletAddress, senderWalletAddressDetails] =
    await getWalletAddressInfo(client, sender_wallet_address);

  // create incoming payment
  const incomingPayment = await createStandardIncomingPayment(
    client,
    receiveAmount!,
    receiverWalletAddressDetails,
  );

  console.log('recurring payment with interest: \n', incomingPayment)

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

    return {outgoingPayment: outgoingPayment, manageurl: manageurl, token: used_token};
  } catch (error) {
    console.log(error);
    return {
      id: "",
      walletAddress: senderWalletAddress,
      quoteId: quote.id,
      failed: true,
      receiver: "",
      // receiveAmount: tokenAccessDetails[0]?.limits?.receiveAmount,
      // debitAmount: tokenAccessDetails[0]?.limits?.debitAmount,
      // sentAmount: tokenAccessDetails[0]?.limits?.debitAmount,
      createdAt: "",
      updatedAt: "",
    } as OutgoingPaymentWithSpentAmounts;
  }
}

// standard payment







