// server.js
import express from 'express';
import { createAuthenticatedClient, isPendingGrant,  isFinalizedGrant,
  OpenPaymentsClientError, } from '@interledger/open-payments';
import config from './config.js';

const app = express();
const port = 3000;

app.use(express.json()); // To parse JSON request bodies

// Endpoint to initiate the payment process
app.post('/create-payment', async (req, res) => {
  const { sender_url, receiver_url, amount } = req.body;

  if (!sender_url || !receiver_url || !amount) {
    return res.status(400).send('sender_url, receiver_url, and amount are required.');
  }

  try {
    const client = await createAuthenticatedClient({
      walletAddressUrl: config.CLIENT_WALLET_ADDRESS_URL,
      keyId: config.KEY_ID,
      privateKey: config.PRIVATE_KEY_PATH,
      validateResponses: false, // Set to false if there are YAML issues
    });

    // Get receiving wallet address details
    const receivingWalletAddress = await client.walletAddress.get({
      url: receiver_url,
    });

    // Get sending wallet address details
    const sendingWalletAddress = await client.walletAddress.get({
      url: sender_url,
    });

    console.log('Received wallet addresses:', {
      receivingWalletAddress,
      sendingWalletAddress,
    });

    // Step 1: Get incoming payment grant for the receiving wallet address
    const incomingPaymentGrant = await client.grant.request(
      {
        url: receivingWalletAddress.authServer,
      },
      {
        access_token: {
          access: [
            {
              type: 'incoming-payment',
              actions: ['read', 'complete', 'create'],
            },
          ],
        },
      }
    );

    if (isPendingGrant(incomingPaymentGrant)) {
      throw new Error('Expected non-interactive grant for incoming payment');
    }

    console.log('Step 1: Got incoming payment grant:', incomingPaymentGrant);

    // Step 2: Create incoming payment on receiving wallet
    const incomingPayment = await client.incomingPayment.create(
      {
        url: receivingWalletAddress.resourceServer,
        accessToken: incomingPaymentGrant.access_token.value,
      },
      {
        walletAddress: receivingWalletAddress.id,
        incomingAmount: {
          value: amount.toString(),
          assetCode: receivingWalletAddress.assetCode,
          assetScale: receivingWalletAddress.assetScale,
        },
        metadata: {
          description: 'Payment from demo',
        },
        expiresAt: new Date(Date.now() + 60_000 * 10).toISOString(), // 10-minute expiration
      }
    );

    console.log('Step 2: Created incoming payment:', incomingPayment);

    // Step 3: Get quote grant for the sending wallet
    const quoteGrant = await client.grant.request(
      {
        url: sendingWalletAddress.authServer,
      },
      {
        access_token: {
          access: [
            {
              type: 'quote',
              actions: ['read', 'create'],
            },
          ],
        },
      }
    );

    if (isPendingGrant(quoteGrant)) {
      throw new Error('Expected non-interactive grant for quote');
    }

    console.log('Step 3: Got quote grant:', quoteGrant);

    // Step 4: Create a quote on the sending wallet
    const quote = await client.quote.create(
      {
        url: sendingWalletAddress.resourceServer,
        accessToken: quoteGrant.access_token.value,
      },
      {
        method: 'ilp',
        walletAddress: sendingWalletAddress.id,
        receiver: incomingPayment.id,
      }
    );

    console.log('Step 4: Created quote:', quote);

    // Step 5: Start the grant process for the outgoing payment (requires user interaction)
    const outgoingPaymentGrant = await client.grant.request(
      {
        url: sendingWalletAddress.authServer,
      },
      {
        access_token: {
          access: [
            {
              identifier: sendingWalletAddress.id,
              type: 'outgoing-payment',
              actions: ['list', 'list-all', 'read', 'read-all', 'create'],
              limits: {
                debitAmount: quote.debitAmount,
              },
            },
          ],
        },
        interact: {
          start: ['redirect'],
        },
      }
    );

    if (!isPendingGrant(outgoingPaymentGrant)) {
      throw new Error('Expected interactive grant');
    }

    console.log('Step 5: Got pending outgoing payment grant:', outgoingPaymentGrant);

    // Output important variables for step 2
    const response = {
      QUOTE_ID: quote.id,
      CONTINUE_URI: outgoingPaymentGrant.continue.uri,
      CONTINUE_ACCESS_TOKEN: outgoingPaymentGrant.continue.access_token.value,
      INTERACT_REDIRECT_URL: outgoingPaymentGrant.interact.redirect,
    };

    res.status(200).json({
      message: 'Proceed with user interaction to finalize the payment',
      response,
    });

    console.log("\nSave the following in the step-2.js script:");
    console.log("QUOTE_URL:", quote.id);
    console.log("CONTINUE_URI:", outgoingPaymentGrant.continue.uri);
    console.log(
      "CONTINUE_ACCESS_TOKEN:",
      outgoingPaymentGrant.continue.access_token.value
    );
  
    
  // // Step 6: Check if the interactive grant was accepted.
  // // If it was, this will return an access token which we can use to create the outgoing payment.
  // let finalizedOutgoingPaymentGrant;

  // try {
  //   finalizedOutgoingPaymentGrant = await client.grant.continue({
  //     accessToken: outgoingPaymentGrant.continue.access_token.value,
  //     url: outgoingPaymentGrant.continue.uri,
  //   });
  // } catch (err) {
  //   if (err instanceof OpenPaymentsClientError && err.status === 401) {
  //     console.log(
  //       "\nThere was an error continuing the grant. You probably have not accepted the grant at the url (or it has already been used up, in which case, you can just rerun the first script)."
  //     );
  //   }
  //   return;
  // }

  // if (!isFinalizedGrant(finalizedOutgoingPaymentGrant)) {
  //   throw new Error(
  //     "Expected finalized grant. Probably the interaction from the previous script was not accepted, or the grant was already used."
  //   );
  // }

  // console.log(
  //   "\nStep 6: Got finalized outgoing payment grant",
  //   finalizedOutgoingPaymentGrant
  // );

  // // Step 7: Finally, create the outgoing payment on the sending wallet address.
  // // This will make a payment from the outgoing payment to the incoming one (over ILP)
  // const outgoingPayment = await client.outgoingPayment.create(
  //   {
  //     url: sendingWalletAddress.resourceServer,
  //     accessToken: finalizedOutgoingPaymentGrant.access_token.value,
  //   },
  //   {
  //     walletAddress: sendingWalletAddress.id,
  //     quoteId: quote.id,
  //   }
  // );

  // console.log(
  //   "\nStep 7: Created outgoing payment. Funds will now move from the outgoing payment to the incoming payment.",
  //   outgoingPayment
  // );
  
  
  } catch (error) {
    console.error('Error creating payment:', error);
    res.status(500).json({ error: error.message });
  }
});


// New endpoint to finish the payment process
app.post('/finish-payment', async (req, res) => {
  const { quoteId, continueUri, continueAccessToken, sendingWalletAddressUrl } = req.body;

  if (!quoteId || !continueUri || !continueAccessToken || !sendingWalletAddressUrl) {
    return res.status(400).send('quoteId, continueUri, continueAccessToken, and sendingWalletAddressUrl are required.');
  }

  try {
    const client = await createAuthenticatedClient({
      walletAddressUrl: config.CLIENT_WALLET_ADDRESS_URL,
      keyId: config.KEY_ID,
      privateKey: config.PRIVATE_KEY_PATH,
      validateResponses: false,
    });

    const sendingWalletAddress = await client.walletAddress.get({
      url: sendingWalletAddressUrl,
    });

    const finalizedOutgoingPaymentGrant = await client.grant.continue({
      accessToken: continueAccessToken,
      url: continueUri,
    });

    if (!isFinalizedGrant(finalizedOutgoingPaymentGrant)) {
      throw new Error("Expected finalized grant. The grant might not be accepted or might be already used.");
    }

    const outgoingPayment = await client.outgoingPayment.create(
      {
        url: sendingWalletAddress.resourceServer,
        accessToken: finalizedOutgoingPaymentGrant.access_token.value,
      },
      {
        walletAddress: sendingWalletAddress.id,
        quoteId: quoteId,
      }
    );

    res.json({ outgoingPayment });

  } catch (err) {
    if (err instanceof OpenPaymentsClientError && err.status === 401) {
      res.status(401).json({ error: 'Grant not accepted or expired' });
    } else {
      res.status(500).json({ error: 'Internal server error', details: err.message });
    }
  }
});


// Start the server
app.listen(port, () => {
  console.log(`Server running on http://localhost:${port}`);
});



