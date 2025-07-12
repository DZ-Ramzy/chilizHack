const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("LeaderboardRewards", function () {
  let LeaderboardRewards;
  let leaderboardRewards;
  let owner;
  let winner1;
  let winner2;
  let winner3;
  let nonWinner;
  let fanToken;

  beforeEach(async function () {
    // Get signers
    [owner, winner1, winner2, winner3, nonWinner] = await ethers.getSigners();

    // Deploy mock FAN token for testing
    const MockToken = await ethers.getContractFactory("MockERC20");
    fanToken = await MockToken.deploy("FAN Token", "FAN");
    await fanToken.deployed();

    // Deploy LeaderboardRewards contract
    LeaderboardRewards = await ethers.getContractFactory("LeaderboardRewards");
    leaderboardRewards = await LeaderboardRewards.deploy();
    await leaderboardRewards.deployed();

    // Mint some tokens to the contract
    await fanToken.mint(leaderboardRewards.address, ethers.utils.parseEther("1000"));
  });

  describe("Deployment", function () {
    it("Should set the correct owner", async function () {
      expect(await leaderboardRewards.owner()).to.equal(owner.address);
    });

    it("Should have the correct FAN token address", async function () {
      expect(await leaderboardRewards.FAN_TOKEN_ADDRESS()).to.equal(fanToken.address);
    });
  });

  describe("Admin Functions", function () {
    it("Should allow owner to set winners", async function () {
      const winners = [winner1.address, winner2.address, winner3.address];
      await leaderboardRewards.setWinners(winners);
      
      const storedWinners = await leaderboardRewards.getWinners();
      expect(storedWinners).to.deep.equal(winners);
    });

    it("Should not allow non-owner to set winners", async function () {
      const winners = [winner1.address, winner2.address];
      await expect(
        leaderboardRewards.connect(winner1).setWinners(winners)
      ).to.be.revertedWith("Ownable: caller is not the owner");
    });

    it("Should allow owner to set reward amount", async function () {
      const rewardAmount = ethers.utils.parseEther("100");
      await leaderboardRewards.setRewardAmount(rewardAmount);
      
      expect(await leaderboardRewards.rewardPerWinner()).to.equal(rewardAmount);
    });

    it("Should not allow non-owner to set reward amount", async function () {
      const rewardAmount = ethers.utils.parseEther("100");
      await expect(
        leaderboardRewards.connect(winner1).setRewardAmount(rewardAmount)
      ).to.be.revertedWith("Ownable: caller is not the owner");
    });
  });

  describe("Winner Functions", function () {
    beforeEach(async function () {
      // Set up winners and reward amount
      const winners = [winner1.address, winner2.address, winner3.address];
      await leaderboardRewards.setWinners(winners);
      await leaderboardRewards.setRewardAmount(ethers.utils.parseEther("100"));
    });

    it("Should allow winners to claim rewards", async function () {
      const initialBalance = await fanToken.balanceOf(winner1.address);
      
      await leaderboardRewards.connect(winner1).claimReward();
      
      const finalBalance = await fanToken.balanceOf(winner1.address);
      expect(finalBalance.sub(initialBalance)).to.equal(ethers.utils.parseEther("100"));
    });

    it("Should not allow non-winners to claim rewards", async function () {
      await expect(
        leaderboardRewards.connect(nonWinner).claimReward()
      ).to.be.revertedWith("LeaderboardRewards: caller is not a winner");
    });

    it("Should not allow double claiming", async function () {
      await leaderboardRewards.connect(winner1).claimReward();
      
      await expect(
        leaderboardRewards.connect(winner1).claimReward()
      ).to.be.revertedWith("LeaderboardRewards: reward already claimed");
    });

    it("Should mark winners as claimed after claiming", async function () {
      await leaderboardRewards.connect(winner1).claimReward();
      
      expect(await leaderboardRewards.hasClaimed(winner1.address)).to.be.true;
    });
  });

  describe("View Functions", function () {
    beforeEach(async function () {
      const winners = [winner1.address, winner2.address, winner3.address];
      await leaderboardRewards.setWinners(winners);
      await leaderboardRewards.setRewardAmount(ethers.utils.parseEther("100"));
    });

    it("Should return correct winner count", async function () {
      expect(await leaderboardRewards.getWinnerCount()).to.equal(3);
    });

    it("Should correctly identify winners", async function () {
      expect(await leaderboardRewards.isWinner(winner1.address)).to.be.true;
      expect(await leaderboardRewards.isWinner(nonWinner.address)).to.be.false;
    });

    it("Should return correct total reward amount", async function () {
      const totalAmount = await leaderboardRewards.getTotalRewardAmount();
      expect(totalAmount).to.equal(ethers.utils.parseEther("300")); // 3 winners * 100 tokens
    });

    it("Should return correct unclaimed rewards", async function () {
      let unclaimed = await leaderboardRewards.getUnclaimedRewards();
      expect(unclaimed).to.equal(ethers.utils.parseEther("300"));

      await leaderboardRewards.connect(winner1).claimReward();
      
      unclaimed = await leaderboardRewards.getUnclaimedRewards();
      expect(unclaimed).to.equal(ethers.utils.parseEther("200"));
    });
  });

  describe("Withdrawal", function () {
    it("Should allow owner to withdraw tokens", async function () {
      const withdrawAmount = ethers.utils.parseEther("100");
      const initialBalance = await fanToken.balanceOf(owner.address);
      
      await leaderboardRewards.withdrawTokens(owner.address, withdrawAmount);
      
      const finalBalance = await fanToken.balanceOf(owner.address);
      expect(finalBalance.sub(initialBalance)).to.equal(withdrawAmount);
    });

    it("Should not allow non-owner to withdraw tokens", async function () {
      const withdrawAmount = ethers.utils.parseEther("100");
      await expect(
        leaderboardRewards.connect(winner1).withdrawTokens(winner1.address, withdrawAmount)
      ).to.be.revertedWith("Ownable: caller is not the owner");
    });
  });
});

// Mock ERC20 token for testing
const MockERC20 = `
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract MockERC20 is ERC20 {
    constructor(string memory name, string memory symbol) ERC20(name, symbol) {}

    function mint(address to, uint256 amount) external {
        _mint(to, amount);
    }
}
`; 