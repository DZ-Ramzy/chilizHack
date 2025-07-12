const { ethers } = require("hardhat");

async function main() {
  console.log("🧪 Testing StakingRewards Contract...\n");

  // Get signers for testing
  const signers = await ethers.getSigners();
  const owner = signers[0];
  
  // Check if we have enough signers and assign users
  console.log(`Available signers: ${signers.length}`);
  let user1, user2;
  
  if (signers.length < 2) {
    console.log("⚠️ Not enough signers available for testing");
    console.log("Using owner for all tests...");
    user1 = owner;
    user2 = owner;
  } else {
    user1 = signers[1];
    user2 = signers[2];
  }
  
  console.log(`Owner: ${owner.address}`);
  console.log(`User1: ${user1.address}`);
  console.log(`User2: ${user2.address}\n`);
  
  // Contract addresses - UPDATE THESE AFTER DEPLOYMENT
  const STAKING_REWARDS_ADDRESS = "0x1A590E1752bE9c2e2524Af21Ff3451ceE9631395"; // StakingRewards contract address
  const FAN_TOKEN_ADDRESS = "0x1F0a316ba43224D87d7024C312Ff52E1c8A2CED9";

  console.log("🔍 Connecting to contracts...");
  console.log(`StakingRewards Address: ${STAKING_REWARDS_ADDRESS}`);
  console.log(`FAN Token Address: ${FAN_TOKEN_ADDRESS}`);

  const stakingRewards = await ethers.getContractAt("StakingRewards", STAKING_REWARDS_ADDRESS);
  const fanToken = await ethers.getContractAt("IERC20", FAN_TOKEN_ADDRESS);

  console.log("📋 Contract Information:");
  console.log(`Owner: ${await stakingRewards.owner()}`);
  console.log(`FAN Token: ${await stakingRewards.FAN_TOKEN_ADDRESS()}`);
  console.log(`Total Levels: ${await stakingRewards.totalLevels()}\n`);

  try {
    // Test 1: Vérifier les niveaux
    console.log("1️⃣ Checking levels...");
    for (let i = 0; i < 11; i++) {
      const levelInfo = await stakingRewards.getLevelInfo(i);
      console.log(`Level ${i}: ${levelInfo.name} - ${levelInfo.minQuests.toString()} quêtes - ${Number(levelInfo.apy)/100}% APY`);
    }
    console.log();

    // Test 2: Vérifier les informations initiales
    console.log("2️⃣ Checking initial info...");
    const totalInfo = await stakingRewards.getTotalInfo();
    console.log(`Total Staked: ${ethers.formatEther(totalInfo._totalStaked)} FAN`);
    console.log(`Total Rewards Distributed: ${ethers.formatEther(totalInfo._totalRewardsDistributed)} FAN`);
    console.log(`Contract Balance: ${ethers.formatEther(totalInfo._contractBalance)} FAN\n`);

    // Test 3: Simuler des quêtes complétées
    console.log("3️⃣ Simulating quest completions...");
    await stakingRewards.connect(owner).completeQuest(user1.address);
    await stakingRewards.connect(owner).completeQuest(user1.address);
    await stakingRewards.connect(owner).completeQuest(user1.address);
    await stakingRewards.connect(owner).completeQuest(user1.address);
    await stakingRewards.connect(owner).completeQuest(user1.address);
    console.log("✅ 5 quests completed for user1\n");

    // Test 4: Vérifier le niveau de l'utilisateur
    console.log("4️⃣ Checking user level...");
    const userStake = await stakingRewards.getUserStake(user1.address);
    console.log(`User1 Level: ${userStake.userLevel.toString()} (${userStake.levelName})`);
    console.log(`Quests Completed: ${userStake.questsCompleted.toString()}`);
    console.log(`APY: ${Number(await stakingRewards.getUserAPY(user1.address))/100}%\n`);

    // Test 5: Simuler du staking (si l'utilisateur a des tokens)
    console.log("5️⃣ Testing staking functionality...");
    const userBalance = await fanToken.balanceOf(user1.address);
    console.log(`User1 FAN Balance: ${ethers.formatEther(userBalance)} FAN`);
    
    if (userBalance > 0n) {
      const stakeAmount = ethers.parseEther("100"); // 100 FAN
      if (userBalance >= stakeAmount) {
        // Approve tokens
        await fanToken.connect(user1).approve(stakingRewards.address, stakeAmount);
        console.log("✅ Tokens approved for staking");
        
        // Stake tokens
        await stakingRewards.connect(user1).stake(stakeAmount);
        console.log("✅ Tokens staked successfully");
        
        // Check staking info
        const newUserStake = await stakingRewards.getUserStake(user1.address);
        console.log(`Staked Amount: ${ethers.formatEther(newUserStake.stakedAmount)} FAN`);
        console.log(`Pending Rewards: ${ethers.formatEther(newUserStake.pendingRewards)} FAN`);
        console.log(`Is Staking: ${newUserStake.isStaking}\n`);
      } else {
        console.log("⚠️ User doesn't have enough tokens for staking test\n");
      }
    } else {
      console.log("⚠️ User has no FAN tokens for staking test\n");
    }

    // Test 6: Simuler plus de quêtes pour monter de niveau
    console.log("6️⃣ Simulating level up...");
    for (let i = 0; i < 10; i++) {
      await stakingRewards.connect(owner).completeQuest(user1.address);
    }
    
    const updatedUserStake = await stakingRewards.getUserStake(user1.address);
    console.log(`New Level: ${updatedUserStake.userLevel.toString()} (${updatedUserStake.levelName})`);
    console.log(`New APY: ${Number(await stakingRewards.getUserAPY(user1.address))/100}%\n`);

    // Test 7: Vérifier les informations finales
    console.log("7️⃣ Checking final info...");
    const finalTotalInfo = await stakingRewards.getTotalInfo();
    console.log(`Final Total Staked: ${ethers.formatEther(finalTotalInfo._totalStaked)} FAN`);
    console.log(`Final Contract Balance: ${ethers.formatEther(finalTotalInfo._contractBalance)} FAN\n`);

    console.log("🎉 All staking tests completed successfully!");
    console.log("\n📊 Final Status:");
    console.log(`Total Staked: ${ethers.formatEther(finalTotalInfo._totalStaked)} FAN`);
    console.log(`User1 Level: ${updatedUserStake.userLevel.toString()} (${updatedUserStake.levelName})`);
    console.log(`User1 APY: ${Number(await stakingRewards.getUserAPY(user1.address))/100}%`);

  } catch (error) {
    console.error("❌ Test failed:", error.message);
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  }); 