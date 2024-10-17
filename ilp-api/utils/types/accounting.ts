export type grantAccessRequest =
  | {
      type: "incoming-payment";
      actions: ("read" | "create" | "complete")[];
    }
  | {
      type: "outgoing-payment";
      actions: ("read" | "create" | "read-all" | "list" | "list-all")[];
      identifier: string;
      limits?: {
        debitAmount?: {
          value: string;
          assetCode: string;
          assetScale: number;
        };
        receiveAmount?: {
          value: string;
          assetCode: string;
          assetScale: number;
        };
        interval?: string; // ISO 8601 recurring interval string
      };
    }
  | {
      type: "quote";
      actions: ("read" | "create" | "read-all")[];
    };

export type incomingPaymentAccessRequest = {
  walletAddress: string;
  incomingAmount: {
    value: string;
    assetCode: string;
    assetScale: number;
  };
  expiresAt: string;
};

export type quoteAccessRequest = {
  method: "ilp";
  walletAddress: string;
  receiver: string;
};

export type Limits = {
  debitAmount?: {
    value: string;
    assetCode: string;
    assetScale: number;
  };
  receiveAmount?: {
    value: string;
    assetCode: string;
    assetScale: number;
  };
  interval?: string; // ISO 8601 recurring interval string
};
