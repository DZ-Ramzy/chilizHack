const { ethers } = require("hardhat");

async function main() {
  console.log("💰 Funding LeaderboardRewards Contract with FAN tokens...\n");

  // Contract addresses - UPDATE THESE AFTER DEPLOYMENT
  const LEADERBOARD_REWARDS_ADDRESS = "0xb6D609B43Dac155e5241d3c20E07225be2c37108"; // Adresse du contrat déployé
  const FAN_TOKEN_ADDRESS = "0x1F0a316ba43224D87d7024C312Ff52E1c8A2CED9";

  // Get signers
  const [owner] = await ethers.getSigners();

  // Get contract instances
  const fanToken = await ethers.getContractAt("IERC20", FAN_TOKEN_ADDRESS);

  console.log("📋 Account Information:");
  console.log(`Owner: ${owner.address}`);
  console.log(`Owner FAN Balance: ${ethers.formatEther(await fanToken.balanceOf(owner.address))} FAN`);
  console.log(`Contract Address: ${LEADERBOARD_REWARDS_ADDRESS}`);
  console.log(`Contract FAN Balance: ${ethers.formatEther(await fanToken.balanceOf(LEADERBOARD_REWARDS_ADDRESS))} FAN\n`);

  try {
    // Transfer FAN tokens to contract
    const transferAmount = ethers.parseEther("1000"); // 1000 FAN tokens
    console.log(`🔄 Transferring ${ethers.formatEther(transferAmount)} FAN to contract...`);
    
    const tx = await fanToken.transfer(LEADERBOARD_REWARDS_ADDRESS, transferAmount);
    await tx.wait();
    
    console.log("✅ Transfer completed successfully!");
    console.log(`Contract new balance: ${ethers.formatEther(await fanToken.balanceOf(LEADERBOARD_REWARDS_ADDRESS))} FAN`);
    console.log(`Owner new balance: ${ethers.formatEther(await fanToken.balanceOf(owner.address))} FAN`);

  } catch (error) {
    console.error("❌ Transfer failed:", error.message);
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  }); 