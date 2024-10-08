import { validateWalletAddress, InvalidWalletResponse } from "./wallet";
import { OpenPaymentsClientError } from "@interledger/open-payments";
import { client } from "./client";
import { warning } from "framer-motion";

export const getWalletBalance = async (walletAddress: string) => {
  try {
    const wallet = await validateWalletAddress(walletAddress);
    console.log("Valid Wallet Address:", wallet);
    // Proceed with fetching the balance using wallet data
    // For example: return await fetchWalletBalance(wallet);
    return wallet; // Replace with actual logic to get balance.
  } catch (error) {
    console.error("Wallet Address Validation Failed:", {
      ...(error as Object), // This includes status and description if present.
      walletAddress: walletAddress,
    });
    return null;
  }
};

const result = await getWalletBalance("https://ilp.rafiki.money/test_account");
console.log(result);
