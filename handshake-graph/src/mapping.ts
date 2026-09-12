import { BigInt } from "@graphprotocol/graph-ts";
import {
  ObjectRegistered,
  CustodyTransferred,
} from "../generated/objcustody/objcustody";
import { Object, CustodyTransfer } from "../generated/schema";

export function handleObjectRegistered(event: ObjectRegistered): void {
  let obj = new Object(event.params.objectId);
  obj.label = event.params.label;
  obj.currentHolder = event.params.initialHolder;
  obj.registeredAt = event.block.timestamp;
  obj.transferCount = 0;
  obj.save();
}

export function handleCustodyTransferred(event: CustodyTransferred): void {
  let obj = Object.load(event.params.objectId);
  if (obj == null) {
    return;
  }
  obj.currentHolder = event.params.to;
  obj.lastTransferAt = event.block.timestamp;
  obj.transferCount = obj.transferCount + 1;
  obj.save();

  let transferId = event.transaction.hash.concatI32(event.logIndex.toI32());
  let transfer = new CustodyTransfer(transferId);
  transfer.object = event.params.objectId;
  transfer.from = event.params.from;
  transfer.to = event.params.to;
  transfer.timestamp = event.block.timestamp;
  transfer.blockNumber = event.block.number;
  transfer.save();
}
