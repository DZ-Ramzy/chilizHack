require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: {
    version: "0.8.19",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200,
      },
    },
  },
  networks: {
    chilizSpicy: {
      url: "https://spicy-rpc.chiliz.com",
      chainId: 88882,
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [],
    },
  },
  etherscan: {
    apiKey: {
      chilizSpicy: "not-needed", // Chiliz doesn't use Etherscan
    },
    customChains: [
      {
        network: "chilizSpicy",
        chainId: 88882,
        urls: {
          apiURL: "https://explorer.chiliz.com/api",
          browserURL: "https://explorer.chiliz.com",
        },
      },
    ],
  },
}; 