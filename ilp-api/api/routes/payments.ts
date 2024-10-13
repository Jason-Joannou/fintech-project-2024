import express, { Response, Request } from "express";
import { client } from "../../utils/ilp-utils/client";
import { validateWalletAddress } from "../../utils/ilp-utils/wallet";
import {
  createGrant,
  createIncomingPayment,
  createQuote,
  createRecurringGrant,
  createRecurringGrantWithStokvelLimits,
} from "../../utils/ilp-utils/paymentTypes";
import {
  GrantType,
  recurringGrantType,
  recurringGrantPayments,
} from "../../utils/types/validation";
import { Grant } from "@interledger/open-payments";
import { executeRecurringPayments } from "../../utils/ilp-utils/payments";

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
      length_between_periods,
      payment_period_length,
      user_id,
      stokvel_id,
    } = req.body; // Get data from request body

    const recieverWallet = await validateWalletAddress(walletAddressURL);
    const senderWallet = await validateWalletAddress(sender_walletAddressURL);

    const grant = await createGrant(
      walletAddressURL,
      GrantType.IncomingPayment,
      false,
      {}
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
      length_between_periods: length_between_periods,
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
      length_between_periods,
      payment_period_length,
      user_id,
      stokvel_id,
    } = req.body; // Get data from request body

    const recieverWallet = await validateWalletAddress(walletAddressURL);
    const senderWallet = await validateWalletAddress(sender_walletAddressURL);

    const grant = await createGrant(
      walletAddressURL,
      GrantType.IncomingPayment,
      false,
      {}
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
      length_between_periods: length_between_periods,
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
      const recurringPayment = executeRecurringPayments(
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

export default router;
