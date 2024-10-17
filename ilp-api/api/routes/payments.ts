import express, { Response, Request } from "express";
import { validateWalletAddress } from "../../utils/ilp-utils/wallet";
import {
  createGrant,
  createIncomingPayment,
  createInitialOutgoingPayment,
  createQuote,
  createRecurringGrant,
  createRecurringGrantWithStokvelLimits,
} from "../../utils/ilp-utils/paymentTypes";
import {
  GrantType,
  recurringGrantType,
  recurringGrantPayments,
  recurringGrantPaymentsWithInterest,
  outgoingPaymentType,
} from "../../utils/types/validation";
import { Grant } from "@interledger/open-payments";
import {
  executeRecurringPayments,
  executeRecurringPaymentsWithInterest,
} from "../../utils/ilp-utils/payments";
import { Limits } from "../../utils/types/accounting";

const router = express.Router();

/**
 * @swagger
 * /payments:
 *   get:
 *     summary: Payments Base Endpoint
 *     description: Returns a welcome message for the payments API.
 *     tags:
 *       - Payments
 *     responses:
 *       200:
 *         description: A JSON object containing a welcome message.
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 message:
 *                   type: string
 *                   example: "Welcome to the payments API! This is the base endpoint."
 */
router.get("/", (req: Request, res: Response) => {
  res.json({
    message: "Welcome to the payments API! This is the base endpoint.",
  });
});

/**
 * @swagger
 * /payments/user_payment_setup:
 *   post:
 *     summary: Set Up User Payment for Stokvel Contributions
 *     description: Creates a user payment setup, including grant creation, incoming payment, and recurring grant for stokvel contributions.
 *     tags:
 *       - Payments
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               value:
 *                 type: number
 *                 description: The total value of the payment setup.
 *               stokvel_contributions_start_date:
 *                 type: string
 *                 format: date
 *                 description: The start date for stokvel contributions.
 *               walletAddressURL:
 *                 type: string
 *                 description: URL for the receiver's wallet address.
 *               sender_walletAddressURL:
 *                 type: string
 *                 description: URL for the sender's wallet address.
 *               payment_periods:
 *                 type: string
 *                 description: The periods during which payments are scheduled (e.g., weekly, monthly).
 *               number_of_periods:
 *                 type: integer
 *                 description: The total number of periods for the payment.
 *               payment_period_length:
 *                 type: string
 *                 description: The length of each payment period (e.g., 7 days, 1 month).
 *               user_id:
 *                 type: string
 *                 description: ID of the user setting up the payment.
 *               stokvel_id:
 *                 type: string
 *                 description: ID of the stokvel to which the payment belongs.
 *               user_contribution:
 *                 type: number
 *                 description: The contribution amount from the user per period.
 *     responses:
 *       200:
 *         description: Successfully created user payment setup.
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 recurring_grant:
 *                   type: object
 *                   description: Details of the created recurring grant.
 *                 continue_uri:
 *                   type: string
 *                   description: URI to continue the recurring grant setup.
 *                 continue_token:
 *                   type: string
 *                   description: Access token to continue the recurring grant setup.
 *                 quote_id:
 *                   type: string
 *                   description: ID of the created quote.
 *       500:
 *         description: Internal server error occurred during grant creation.
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 error:
 *                   type: string
 *                   example: "An unexpected error occurred during grant creation."
 */
router.post("/user_payment_setup", async (req: Request, res: Response) => {
  try {
    const {
      value,
      stokvel_contributions_start_date,
      walletAddressURL,
      sender_walletAddressURL,
      payment_periods,
      number_of_periods,
      payment_period_length,
      user_id,
      stokvel_id,
      user_contribution,
    } = req.body; // Get data from request body

    const recieverWallet = await validateWalletAddress(walletAddressURL);
    const senderWallet = await validateWalletAddress(sender_walletAddressURL);

    const grant = await createGrant(
      recieverWallet,
      GrantType.IncomingPayment,
      false,
      "user",
      {},
      user_id,
      stokvel_id
    );

    const incomingPayment = await createIncomingPayment(
      recieverWallet,
      value,
      grant as Grant,
      stokvel_contributions_start_date
    );

    const quote = await createQuote(senderWallet, incomingPayment.id);

    const authParameters: recurringGrantType = {
      senderWalletAddress: senderWallet,
      stokvelContributionStartDate: stokvel_contributions_start_date,
      payment_periods: payment_periods,
      payment_period_length: payment_period_length,
      number_of_periods: number_of_periods,
      quote_id: quote.id,
      debitAmount: {
        value: user_contribution,
        assetCode: quote.debitAmount.assetCode,
        assetScale: quote.debitAmount.assetScale,
      },
      receiveAmount: {
        value: user_contribution,
        assetCode: quote.receiveAmount.assetCode,
        assetScale: quote.receiveAmount.assetScale,
      },
      user_id: user_id,
      stokvel_id: stokvel_id,
    };
    const recurringGrant = await createRecurringGrant(authParameters);

    res.json({
      recurring_grant: recurringGrant,
      continue_uri: recurringGrant.continue.uri,
      continue_token: recurringGrant.continue.access_token,
      quote_id: quote.id,
    });
  } catch (error) {
    console.log(error);
    return res
      .status(500)
      .json({ error: "An unexpected error occurred during grant creation." });
  }
});

/**
 * @swagger
 * /payments/stokvel_payment_setup:
 *   post:
 *     summary: Set Up Stokvel Payment for Contributions
 *     description: Creates a payment setup for stokvel contributions, including grant creation, incoming payment, and recurring grant setup.
 *     tags:
 *       - Payments
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               value:
 *                 type: number
 *                 description: The total value of the payment setup.
 *               stokvel_contributions_start_date:
 *                 type: string
 *                 format: date
 *                 description: The start date for stokvel contributions.
 *               walletAddressURL:
 *                 type: string
 *                 description: URL for the receiver's wallet address.
 *               sender_walletAddressURL:
 *                 type: string
 *                 description: URL for the sender's wallet address.
 *               payment_periods:
 *                 type: string
 *                 description: The periods during which payments are scheduled (e.g., weekly, monthly).
 *               payment_period_length:
 *                 type: string
 *                 description: The length of each payment period (e.g., 7 days, 1 month).
 *               number_of_periods:
 *                 type: integer
 *                 description: The total number of periods for the payment.
 *               user_id:
 *                 type: string
 *                 description: ID of the user setting up the payment.
 *               stokvel_id:
 *                 type: string
 *                 description: ID of the stokvel to which the payment belongs.
 *     responses:
 *       200:
 *         description: Successfully created stokvel payment setup.
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 recurring_grant:
 *                   type: object
 *                   description: Details of the created recurring grant.
 *                 continue_uri:
 *                   type: string
 *                   description: URI to continue the recurring grant setup.
 *                 continue_token:
 *                   type: string
 *                   description: Access token to continue the recurring grant setup.
 *                 quote_id:
 *                   type: string
 *                   description: ID of the created quote.
 *       500:
 *         description: Internal server error occurred during grant creation.
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 error:
 *                   type: string
 *                   example: "An unexpected error occurred during grant creation."
 */
router.post("/stokvel_payment_setup", async (req: Request, res: Response) => {
  try {
    const {
      value,
      stokvel_contributions_start_date,
      walletAddressURL,
      sender_walletAddressURL,
      payment_periods,
      payment_period_length,
      number_of_periods,
      user_id,
      stokvel_id,
    } = req.body; // Get data from request body

    const recieverWallet = await validateWalletAddress(walletAddressURL);
    const senderWallet = await validateWalletAddress(sender_walletAddressURL);

    const grant = await createGrant(
      recieverWallet,
      GrantType.IncomingPayment,
      false,
      "stokvel",
      {},
      user_id,
      stokvel_id
    );

    const incomingPayment = await createIncomingPayment(
      recieverWallet,
      value,
      grant as Grant,
      stokvel_contributions_start_date
    );

    const quote = await createQuote(senderWallet, incomingPayment.id);

    const authParameters: recurringGrantType = {
      senderWalletAddress: senderWallet,
      stokvelContributionStartDate: stokvel_contributions_start_date,
      payment_periods: payment_periods,
      payment_period_length: payment_period_length,
      quote_id: quote.id,
      number_of_periods: number_of_periods,
      debitAmount: {
        value: quote.debitAmount.value,
        assetCode: quote.debitAmount.assetCode,
        assetScale: quote.debitAmount.assetScale,
      },
      receiveAmount: {
        value: quote.receiveAmount.value,
        assetCode: quote.receiveAmount.assetCode,
        assetScale: quote.receiveAmount.assetScale,
      },
      user_id: user_id,
      stokvel_id: stokvel_id,
    };
    const recurringGrant =
      await createRecurringGrantWithStokvelLimits(authParameters);

    res.json({
      recurring_grant: recurringGrant,
      continue_uri: recurringGrant.continue.uri,
      continue_token: recurringGrant.continue.access_token,
      quote_id: quote.id,
    });
  } catch (error) {
    console.log(error);
    return res
      .status(500)
      .json({ error: "An unexpected error occurred during grant creation." });
  }
});

/**
 * @swagger
 * /payments/process_recurring_payments:
 *   post:
 *     summary: Process Recurring Payments
 *     description: Processes recurring payments by using the provided sender and receiver wallet addresses, contribution value, and other parameters.
 *     tags:
 *       - Payments
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               sender_wallet_address:
 *                 type: string
 *                 description: Wallet address of the sender.
 *               receiving_wallet_address:
 *                 type: string
 *                 description: Wallet address of the recipient.
 *               manageUrl:
 *                 type: string
 *                 description: URL to manage the recurring grant.
 *               previousToken:
 *                 type: string
 *                 description: Previous access token to continue the recurring payment.
 *               contributionValue:
 *                 type: number
 *                 description: The value of the contribution for this payment period.
 *     responses:
 *       200:
 *         description: Successfully processed recurring payment.
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 status:
 *                   type: string
 *                   example: "success"
 *                 message:
 *                   type: string
 *                   description: Result of the payment process.
 *       500:
 *         description: Internal server error occurred during payment processing.
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 error:
 *                   type: string
 *                   example: "An unexpected error occurred during grant creation."
 */
router.post(
  "/process_recurring_payments",
  async (req: Request, res: Response) => {
    try {
      const {
        sender_wallet_address,
        receiving_wallet_address,
        manageUrl,
        previousToken,
        contributionValue,
      } = req.body; // Get data from request body

      const recurringPaymentParameters: recurringGrantPayments = {
        senderWalletAddress: sender_wallet_address,
        receiverWalletAddress: receiving_wallet_address,
        manageURL: manageUrl,
        previousToken: previousToken,
        contributionValue: contributionValue,
      };
      const recurringPayment = await executeRecurringPayments(
        recurringPaymentParameters
      );

      res.json(recurringPayment);
    } catch (error) {
      console.log(error);
      return res
        .status(500)
        .json({ error: "An unexpected error occurred during grant creation." });
    }
  }
);

/**
 * @swagger
 * /payments/process_recurring_winterest_payment:
 *   post:
 *     summary: Process Recurring Payment with Interest
 *     description: Processes recurring payments that include interest calculations, using sender and receiver wallet addresses.
 *     tags:
 *       - Payments
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               sender_wallet_address:
 *                 type: string
 *                 description: Wallet address of the sender.
 *               receiving_wallet_address:
 *                 type: string
 *                 description: Wallet address of the recipient.
 *               manageUrl:
 *                 type: string
 *                 description: URL to manage the recurring grant.
 *               previousToken:
 *                 type: string
 *                 description: Previous access token to continue the recurring payment.
 *               payout_value:
 *                 type: number
 *                 description: The payout value including interest for this payment period.
 *     responses:
 *       200:
 *         description: Successfully processed recurring payment with interest.
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 status:
 *                   type: string
 *                   example: "success"
 *                 message:
 *                   type: string
 *                   description: Result of the payment process.
 *       500:
 *         description: Internal server error occurred during payment processing.
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 error:
 *                   type: string
 *                   example: "An unexpected error occurred during grant creation."
 */
router.post(
  "/process_recurring_winterest_payment",
  async (req: Request, res: Response) => {
    try {
      const {
        sender_wallet_address,
        receiving_wallet_address,
        manageUrl,
        previousToken,
        payout_value,
      } = req.body; // Get data from request body

      const parameters: recurringGrantPaymentsWithInterest = {
        senderWalletAddress: sender_wallet_address,
        receiverWalletAddress: receiving_wallet_address,
        manageURL: manageUrl,
        previousToken: previousToken,
        payoutValue: payout_value,
      };
      const recurringPaymentWithInterest =
        await executeRecurringPaymentsWithInterest(parameters);

      res.json(recurringPaymentWithInterest);
    } catch (error) {
      console.log(error);
      return res
        .status(500)
        .json({ error: "An unexpected error occurred during grant creation." });
    }
  }
);

/**
 * @swagger
 * /payments/initial_outgoing_payment:
 *   post:
 *     summary: Create Initial Outgoing Payment
 *     description: Sets up an initial outgoing payment, generating a quote and authorization for the sender's wallet.
 *     tags:
 *       - Payments
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               quote_id:
 *                 type: string
 *                 description: ID of the payment quote.
 *               continueUri:
 *                 type: string
 *                 description: URI to continue the outgoing payment setup.
 *               continueAccessToken:
 *                 type: string
 *                 description: Access token to continue the outgoing payment setup.
 *               walletAddressURL:
 *                 type: string
 *                 description: URL of the sender's wallet address.
 *               interact_ref:
 *                 type: string
 *                 description: Reference ID for interaction.
 *     responses:
 *       200:
 *         description: Successfully created initial outgoing payment.
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 payment:
 *                   type: object
 *                   description: Details of the created payment.
 *                 token:
 *                   type: string
 *                   description: Access token for the payment setup.
 *                 manageurl:
 *                   type: string
 *                   description: URL to manage the payment.
 *       500:
 *         description: Internal server error occurred during payment processing.
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 error:
 *                   type: string
 *                   example: "An unexpected error occurred during grant creation."
 */
router.post(
  "/initial_outgoing_payment",
  async (req: Request, res: Response) => {
    try {
      const {
        quote_id,
        continueUri,
        continueAccessToken,
        walletAddressURL,
        interact_ref,
      } = req.body;

      const authParameters: outgoingPaymentType = {
        quote_id: quote_id,
        continueUri: continueUri,
        continueAccessToken: continueAccessToken,
        senderWalletAddress: walletAddressURL,
        interactRef: interact_ref,
      };

      const { payment, token, manageurl } =
        await createInitialOutgoingPayment(authParameters);

      return res.json({ payment: payment, token: token, manageurl: manageurl });
    } catch (error) {
      console.log(error);
      return res
        .status(500)
        .json({ error: "An unexpected error occurred during grant creation." });
    }
  }
);

/**
 * @swagger
 * /payments/adhoc-payment:
 *   post:
 *     summary: Create Adhoc Payment
 *     description: Sets up an adhoc payment, generating a grant, incoming payment, and quote.
 *     tags:
 *       - Payments
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               value:
 *                 type: number
 *                 description: The total value of the adhoc payment.
 *               walletAddressURL:
 *                 type: string
 *                 description: URL for the receiver's wallet address.
 *               sender_walletAddressURL:
 *                 type: string
 *                 description: URL for the sender's wallet address.
 *               user_id:
 *                 type: string
 *                 description: ID of the user initiating the payment.
 *               stokvel_id:
 *                 type: string
 *                 description: ID of the stokvel associated with the payment.
 *     responses:
 *       200:
 *         description: Successfully created adhoc payment.
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 recurring_grant:
 *                   type: object
 *                   description: Details of the created grant.
 *                 continue_uri:
 *                   type: string
 *                   description: URI to continue the grant setup.
 *                 continue_token:
 *                   type: string
 *                   description: Access token to continue the grant setup.
 *                 quote_id:
 *                   type: string
 *                   description: ID of the created quote.
 *       500:
 *         description: Internal server error occurred during grant creation.
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 error:
 *                   type: string
 *                   example: "An unexpected error occurred during grant creation."
 */
router.post("/adhoc-payment", async (req: Request, res: Response) => {
  try {
    const {
      value,
      walletAddressURL,
      sender_walletAddressURL,
      user_id,
      stokvel_id,
    } = req.body; // Get data from request body

    const receiverWallet = await validateWalletAddress(walletAddressURL);
    const senderWallet = await validateWalletAddress(sender_walletAddressURL);

    const paydate = new Date().toISOString();
    const grant = await createGrant(
      receiverWallet,
      GrantType.IncomingPayment,
      false
    );
    const incomingPayment = await createIncomingPayment(
      receiverWallet,
      value,
      grant as Grant,
      paydate
    );
    const quote = await createQuote(senderWallet, incomingPayment.id);
    const paymentLimits: Limits = {
      debitAmount: quote.debitAmount,
      receiveAmount: quote.receiveAmount,
    };
    const recurringGrant = await createGrant(
      senderWallet,
      GrantType.OutgoingPayment,
      true,
      "adhoc",
      paymentLimits,
      user_id,
      stokvel_id,
      quote.id
    );

    res.json({
      recurring_grant: recurringGrant,
      continue_uri: recurringGrant.continue.uri,
      continue_token: recurringGrant.continue.access_token,
      quote_id: quote.id,
    }); //{all information stored here should be returned}
  } catch (error) {
    console.log(error);
    return res
      .status(500)
      .json({ error: "An unexpected error occurred during grant creation." });
  }
});

export default router;
