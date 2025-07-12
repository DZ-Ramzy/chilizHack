const { ethers } = require("hardhat");

async function main() {
  console.log("Deploying LeaderboardRewards contract...");

  // Get the contract factory
  const LeaderboardRewards = await ethers.getContractFactory("LeaderboardRewards");
  
  // Deploy the contract
  const leaderboardRewards = await LeaderboardRewards.deploy();
  
  // Wait for deployment to finish
  await leaderboardRewards.waitForDeployment();

  const contractAddress = await leaderboardRewards.getAddress();
  
  console.log("LeaderboardRewards deployed to:", contractAddress);
  console.log("FAN Token Address:", await leaderboardRewards.FAN_TOKEN_ADDRESS());
  console.log("Owner:", await leaderboardRewards.owner());
  
  // Save deployment info
  const deploymentInfo = {
    contractAddress: contractAddress,
    fanTokenAddress: await leaderboardRewards.FAN_TOKEN_ADDRESS(),
    owner: await leaderboardRewards.owner(),
    network: "Chiliz Spicy Testnet",
    chainId: 88882,
    deployer: (await ethers.getSigners())[0].address
  };
  
  console.log("\nDeployment Info:");
  console.log(JSON.stringify(deploymentInfo, null, 2));
  
  // Save to file for frontend integration
  const fs = require("fs");
  fs.writeFileSync(
    "deployment-info.json", 
    JSON.stringify(deploymentInfo, null, 2)
  );
  console.log("\nDeployment info saved to deployment-info.json");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  }); 