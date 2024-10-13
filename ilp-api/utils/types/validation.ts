import { IWalletAddressResponse } from "./wallet";
export type GrantStatusResult =
  | {
      isPending: true;
      isRejected: false;
      isAccepted: false;
      continueUri: string; // Include the continue URI for pending grants
    }
  | {
      isPending: false;
      isRejected: false;
      isAccepted: true;
    }
  | {
      isPending: false;
      isRejected: true;
      isAccepted: false;
    };

export type AccessRequest =
  | {
      type: "incoming-payment";
      actions: (
        | "read"
        | "create"
        | "complete"
        | "read-all"
        | "list"
        | "list-all"
      )[];
    }
  | {
      type: "outgoing-payment";
      actions: ("read" | "create" | "read-all" | "list" | "list-all")[];
      identifier: string;
    }
  | {
      type: "quote";
      actions: ("read" | "create" | "read-all")[];
    };

export enum GrantType {
  IncomingPayment = "incoming-payment",
  OutgoingPayment = "outgoing-payment",
  Quote = "quote",
}

export type recurringGrantType = {
  senderWalletAddress: IWalletAddressResponse;
  stokvelContributionStartDate: string;
  payment_periods: number;
  payment_period_length: string;
  length_between_periods: string;
  quote_id: string;
  debitAmount: {
    value: string;
    assetCode: string;
    assetScale: number;
  };
  receiveAmount: {
    value: string;
    assetCode: string;
    assetScale: number;
  };
  user_id: number;
  stokvel_id: number;
};

export type outgoingPaymentType = {
  quote_id: string;
  continueUri: string;
  continueAccessToken: string;
  senderWalletAddress: string;
  interactRef?: string;
  tokenValue?: string;
};

export type recurringGrantPayments = {
  senderWalletAddress: string;
  receiverWalletAddress: string;
  manageURL: string;
  previousToken: string;
};

export type recurringGrantPaymentsWithInterest = recurringGrantPayments & {
  payoutValue: string;
};
