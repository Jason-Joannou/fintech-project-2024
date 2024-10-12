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
