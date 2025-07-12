const { ethers } = require("hardhat");

async function main() {
  console.log("Deploying StakingRewards contract...");

  // Get the contract factory
  const StakingRewards = await ethers.getContractFactory("StakingRewards");
  
  // Deploy the contract
  const stakingRewards = await StakingRewards.deploy();
  
  // Wait for deployment to finish
  await stakingRewards.waitForDeployment();

  const contractAddress = await stakingRewards.getAddress();
  
  console.log("StakingRewards deployed to:", contractAddress);
  console.log("FAN Token Address:", await stakingRewards.FAN_TOKEN_ADDRESS());
  console.log("Owner:", await stakingRewards.owner());
  
  // Save deployment info
  const deploymentInfo = {
    contractAddress: contractAddress,
    fanTokenAddress: await stakingRewards.FAN_TOKEN_ADDRESS(),
    owner: await stakingRewards.owner(),
    network: "Chiliz Spicy Testnet",
    chainId: 88882,
    deployer: (await ethers.getSigners())[0].address,
    contractType: "StakingRewards"
  };
  
  console.log("\nDeployment Info:");
  console.log(JSON.stringify(deploymentInfo, null, 2));
  
  // Save to file for frontend integration
  const fs = require("fs");
  fs.writeFileSync(
    "staking-deployment-info.json", 
    JSON.stringify(deploymentInfo, null, 2)
  );
  console.log("\nDeployment info saved to staking-deployment-info.json");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  }); 