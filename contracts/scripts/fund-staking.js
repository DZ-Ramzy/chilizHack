const { ethers } = require("hardhat");

async function main() {
  console.log("💰 Funding StakingRewards Contract...\n");

  // Get signers
  const signers = await ethers.getSigners();
  const owner = signers[0];
  
  // Contract addresses - UPDATE THESE AFTER DEPLOYMENT
  const STAKING_REWARDS_ADDRESS = "0x1A590E1752bE9c2e2524Af21Ff3451ceE9631395"; // StakingRewards contract address
  const FAN_TOKEN_ADDRESS = "0x1F0a316ba43224D87d7024C312Ff52E1c8A2CED9";

  console.log("🔍 Connecting to contracts...");
  console.log(`StakingRewards Address: ${STAKING_REWARDS_ADDRESS}`);
  console.log(`FAN Token Address: ${FAN_TOKEN_ADDRESS}`);

  const stakingRewards = await ethers.getContractAt("StakingRewards", STAKING_REWARDS_ADDRESS);
  const fanToken = await ethers.getContractAt("IERC20", FAN_TOKEN_ADDRESS);

  try {
    // Check owner balance
    const ownerBalance = await fanToken.balanceOf(owner.address);
    console.log(`Owner FAN Balance: ${ethers.formatEther(ownerBalance)} FAN`);

    // Amount to fund the staking contract
    const fundAmount = ethers.parseEther("10000"); // 10,000 FAN tokens
    
    if (ownerBalance.lt(fundAmount)) {
      console.log("❌ Owner doesn't have enough FAN tokens to fund the contract");
      console.log(`Required: ${ethers.formatEther(fundAmount)} FAN`);
      console.log(`Available: ${ethers.formatEther(ownerBalance)} FAN`);
      return;
    }

    // Check current contract balance
    const contractBalanceBefore = await fanToken.balanceOf(stakingRewards.address);
    console.log(`Contract Balance Before: ${ethers.formatEther(contractBalanceBefore)} FAN`);

    // Approve tokens
    console.log("✅ Approving tokens for staking contract...");
    await fanToken.approve(stakingRewards.address, fundAmount);
    console.log("✅ Tokens approved");

    // Add reward tokens to contract
    console.log("✅ Adding reward tokens to contract...");
    await stakingRewards.addRewardTokens(fundAmount);
    console.log("✅ Reward tokens added successfully");

    // Check final contract balance
    const contractBalanceAfter = await fanToken.balanceOf(stakingRewards.address);
    console.log(`Contract Balance After: ${ethers.formatEther(contractBalanceAfter)} FAN`);

    // Set reward rate (example: 1 FAN per day = 1/86400 FAN per second)
    const rewardPerSecond = ethers.parseEther("1") / BigInt(86400); // 1 FAN per day
    console.log("✅ Setting reward rate...");
    await stakingRewards.setRewardPerSecond(rewardPerSecond);
    console.log(`✅ Reward rate set to ${ethers.formatEther(rewardPerSecond)} FAN per second`);

    console.log("\n🎉 Staking contract funded successfully!");
    console.log(`💰 Total funded: ${ethers.formatEther(fundAmount)} FAN`);
    console.log(`📈 Daily reward rate: 1 FAN`);
    console.log(`⏰ Reward per second: ${ethers.formatEther(rewardPerSecond)} FAN`);

  } catch (error) {
    console.error("❌ Funding failed:", error.message);
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  }); 