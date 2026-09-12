type Object @entity(immutable: false) {
  id: Bytes!
  label: String!
  currentHolder: Bytes!
  registeredAt: BigInt!
  lastTransferAt: BigInt
  transferCount: Int!
}

type CustodyTransfer @entity(immutable: true) {
  id: Bytes!
  object: Object!
  from: Bytes!
  to: Bytes!
  timestamp: BigInt!
  blockNumber: BigInt!
}
