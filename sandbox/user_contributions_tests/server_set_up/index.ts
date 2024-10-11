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
  getOutgoingPaymentAuthorization_HugeLimit_StokvelPayout,
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
    const { value, stokvel_contributions_start_date, walletAddressURL, sender_walletAddressURL, 
      payment_periods,length_between_periods, payment_period_length, user_id, stokvel_id } = req.body; // Get data from request body

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
       payment_period_length, length_between_periods ,quote.id, quote.debitAmount, quote.receiveAmount, user_id, stokvel_id)

    // Send back the information about the grant as a JSON response
    res.json({recurring_grant: recurring_grant, continue_uri: recurring_grant.continue.uri, continue_token: recurring_grant.continue.access_token, quote_id: quote.id}); //{all information stored here should be returned}
    
} catch (error: unknown) {  // Specify that error can be of type unknown
  console.error(error);

  // Handle the error safely
  if (error instanceof Error) {
      res.status(500).json({ error: error.message });
  } else {
      res.status(500).json({ error: "An unknown error occurred" });
  }}
});

//create incoming payment
app.post('/incoming-payment-setup-stokvel-payout', async (req: Request, res: Response) => {
  try {
    const { value, stokvel_contributions_start_date, walletAddressURL, 
      sender_walletAddressURL, payment_periods, payment_period_length, number_of_periods,
      user_id, stokvel_id } = req.body; // Get data from request body

    console.log(value)
    console.log('stockvel setup body \n', req.body)

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
    const recurring_grant = await getOutgoingPaymentAuthorization_HugeLimit_StokvelPayout(client, sender_walletFullDetails, stokvel_contributions_start_date, payment_periods,
       payment_period_length, quote.id, quote.debitAmount, quote.receiveAmount, number_of_periods, user_id, stokvel_id)

    // Send back the information about the grant as a JSON response
    res.json({recurring_grant: recurring_grant, continue_uri: recurring_grant.continue.uri, continue_token: recurring_grant.continue.access_token, quote_id: quote.id}); //{all information stored here should be returned}
    
} catch (error: unknown) {  // Specify that error can be of type unknown
  console.error(error);

  // Handle the error safely
  if (error instanceof Error) {
      res.status(500).json({ error: error.message });
  } else {
      res.status(500).json({ error: "An unknown error occurred" });
  }}
});

//create initial outgoing payment
app.post('/create-initial-outgoing-payment', async (req: Request, res: Response) => {
  try {
    const { quote_id, continueUri, continueAccessToken, walletAddressURL, interact_ref } = req.body; // Get data from request body
    
    console.log(walletAddressURL) //this needs to be the sender wallet address
    console.log(continueUri)
    console.log(continueAccessToken)
    console.log(quote_id)

    const client = await getAuthenticatedClient()
    
    const walletFullDetails = await client.walletAddress.get({
      url: walletAddressURL,
    });

    const { payment, token, manageurl } = await createInitialOutgoingPayment(client, quote_id, 
      continueUri, continueAccessToken, walletAddressURL, interact_ref) //sender wallet address
    
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


