import express, {Express, Request, Response} from 'express';
import {
  createStandardIncomingPayment,
  createInitialIncomingPayment,
  createInitialOutgoingPayment,
  processRecurringPayments,
  createQuote,
  getAuthenticatedClient,
  getOutgoingPaymentAuthorization,
  getWalletAddressInfo,
  processInterestAddedRecurringPayments,
} from "./helpers";

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
import { getQuote } from '@interledger/open-payments/dist/client/quote';
import { createOutgoingPayment } from '@interledger/open-payments/dist/client/outgoing-payment';

const app: Express = express();
const port = 3000;


app.use(express.json());

app.get('/', (req: Request, res: Response) => {
  res.send('Hello, JavaScript with Express!');
});

//create incoming payment
app.post('/incoming-payment-setup', async (req: Request, res: Response) => {
  try {
    const { value, stokvel_contributions_start_date, walletAddressURL, sender_walletAddressURL, payment_periods, payment_period_length } = req.body; // Get data from request body

    console.log(value)
    console.log(walletAddressURL)

    const client = await getAuthenticatedClient()
    
    const walletFullDetails = await client.walletAddress.get({ //receiver
      url: walletAddressURL,
    });

    
    const sender_walletFullDetails = await client.walletAddress.get({ //sender
      url: sender_walletAddressURL,
    });
    
    // Call the createStandardIncomingPayment function
    const incomingPayment = await createInitialIncomingPayment(client, value ,walletFullDetails, stokvel_contributions_start_date);
    const quote = await createQuote(client, incomingPayment.id, sender_walletFullDetails)
    const recurring_grant = await getOutgoingPaymentAuthorization(client, sender_walletFullDetails, stokvel_contributions_start_date, payment_periods,
       payment_period_length, quote.id, quote.debitAmount, quote.receiveAmount)

    // Send back the information about the grant as a JSON response
    res.json({recurring_grant: recurring_grant, continue_uri: recurring_grant.continue.uri, continue_token: recurring_grant.continue.access_token}); //{all information stored here should be returned}
    
} catch (error: unknown) {  // Specify that error can be of type unknown
  console.error(error);

  // Handle the error safely
  if (error instanceof Error) {
      res.status(500).json({ error: error.message });
  } else {
      res.status(500).json({ error: "An unknown error occurred" });
  }}
});

/*COMMENTED OUT, BECAUSE...YOU'D ONLY NEED TO USE THE RECURRING GRANT INITIALLY????
//create recurring grant thing
app.post('/create-recurring-grant-request', async (req: Request, res: Response) => {
  try {
    const {
      walletAddressURL,
      stokvel_contributions_start_date,
      payment_periods,
      payment_period_length,
      quote_id,
      // quote_access_token
    } = req.body;

    // Log or use the data
      // console.log(client);
      console.log(walletAddressURL);
      console.log(stokvel_contributions_start_date);
      console.log(payment_periods);
      console.log(payment_period_length);
      console.log(quote_id);
      // console.log(quote_access_token);

    const client = await getAuthenticatedClient()
    
    const walletFullDetails = await client.walletAddress.get({
      url: walletAddressURL,
    });

    
    const pending_recurring_grant = await getOutgoingPaymentAuthorization(
      client, walletFullDetails, stokvel_contributions_start_date, payment_periods,
       payment_period_length, quote_id )
    
    // Send back the incoming payment as a JSON response
    console.log("CONTINUE INFORMATION")
    console.log(pending_recurring_grant.continue.uri)
    console.log(pending_recurring_grant.continue.access_token)

    res.json(pending_recurring_grant);
    return {continue_uri: pending_recurring_grant.continue.uri, continue_token: pending_recurring_grant.continue.access_token}//we need to store this to create the inital payment
} catch (error: unknown) {  // Specify that error can be of type unknown
  console.error(error);

  // Handle the error safely
  if (error instanceof Error) {
      res.status(500).json({ error: error.message });
  } else {
      res.status(500).json({ error: "An unknown error occurred" });
  }}
});*/

//create initial outgoing payment
app.post('/create-initial-outgoing-payment', async (req: Request, res: Response) => {
  try {
    const { quote_id, continueUri, continueAccessToken, walletAddressURL } = req.body; // Get data from request body
    
    console.log(walletAddressURL)
    console.log(continueUri)
    console.log(continueAccessToken)
    console.log(quote_id)

    const client = await getAuthenticatedClient()
    
    const walletFullDetails = await client.walletAddress.get({
      url: walletAddressURL,
    });

    const { payment, token, manageurl } = await createInitialOutgoingPayment(client, quote_id, 
      continueUri, continueAccessToken, walletAddressURL)
    
    // Send back the outgoing payment as a JSON response
    res.json({payment, token: token, manageurl: manageurl});
    return {token, manageurl};

} catch (error: unknown) {  // Specify that error can be of type unknown
  console.error(error);

  // Handle the error safely
  if (error instanceof Error) {
      res.status(500).json({ error: error.message });
  } else {
      res.status(500).json({ error: "An unknown error occurred" });
  }}
});

// completes a payment using an established grant
app.post('/process-recurring-payment', async (req: Request, res: Response) => {
  try {
      const { sender_wallet_address, receiving_wallet_address, manageUrl, previousToken } = req.body; // Get data from request body

    const client = await getAuthenticatedClient()
    
    // const walletFullDetails = await client.walletAddress.get({
    //   url: walletAddressURL,
    // });


    const recurring_payment = await processRecurringPayments(client, sender_wallet_address, receiving_wallet_address, manageUrl, previousToken);
    
    // Send back the incoming payment as a JSON response
    res.json(recurring_payment);
} catch (error: unknown) {  // Specify that error can be of type unknown
  console.error(error);

  // Handle the error safely
  if (error instanceof Error) {
      res.status(500).json({ error: error.message });
  } else {
      res.status(500).json({ error: "An unknown error occurred" });
  }}
});


app.post('/process-recurring-winterest-payment', async (req: Request, res: Response) => {
  try {
      const { sender_wallet_address, receiving_wallet_address, manageUrl, previousToken, payout_value } = req.body; // Get data from request body

    const client = await getAuthenticatedClient()
    
    // const walletFullDetails = await client.walletAddress.get({
    //   url: walletAddressURL,
    // });


    const recurring_payment = await processInterestAddedRecurringPayments(client, sender_wallet_address, receiving_wallet_address, manageUrl, previousToken, payout_value);
    
    // Send back the incoming payment as a JSON response
    res.json(recurring_payment);
} catch (error: unknown) {  // Specify that error can be of type unknown
  console.error(error);

  // Handle the error safely
  if (error instanceof Error) {
      res.status(500).json({ error: error.message });
  } else {
      res.status(500).json({ error: "An unknown error occurred" });
  }}
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});


