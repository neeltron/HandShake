// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ObjectCustody {
    mapping(bytes32 => address) public holderOf;
    mapping(bytes32 => bool) public isRegistered;

    event ObjectRegistered(bytes32 indexed objectId, address indexed initialHolder, string label);
    event CustodyTransferred(bytes32 indexed objectId, address indexed from, address indexed to);

    function registerObject(bytes32 objectId, string calldata label) external {
        require(!isRegistered[objectId], "already registered");
        isRegistered[objectId] = true;
        holderOf[objectId] = msg.sender;
        emit ObjectRegistered(objectId, msg.sender, label);
    }

    function transferCustody(bytes32 objectId, address to) external {
        require(isRegistered[objectId], "not registered");
        require(holderOf[objectId] == msg.sender, "not current holder");
        require(to != address(0), "invalid recipient");

        address from = msg.sender;
        holderOf[objectId] = to;
        emit CustodyTransferred(objectId, from, to);
    }
}