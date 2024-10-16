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

router.get("/", (req: Request, res: Response) => {
  res.json({
    message: "Welcome to the payments API! This is the base endpoint.",
  });
});

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

router.post(
  "/process_recurring_payments",
  async (req: Request, res: Response) => {
    try {
      const {
        sender_wallet_address,
        receiving_wallet_address,
        manageUrl,
        previousToken,
      } = req.body; // Get data from request body

      const recurringPaymentParameters: recurringGrantPayments = {
        senderWalletAddress: sender_wallet_address,
        receiverWalletAddress: receiving_wallet_address,
        manageURL: manageUrl,
        previousToken: previousToken,
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
