# LeaderboardRewards Smart Contract

A Solidity smart contract for managing leaderboard reward distribution using FAN tokens on the Chiliz Spicy Testnet.

## Features

- ✅ Manage up to 10 leaderboard winners
- ✅ Prevent double claiming of rewards
- ✅ Admin controls for setting winners and reward amounts
- ✅ Secure token distribution with reentrancy protection
- ✅ Admin ability to withdraw remaining tokens
- ✅ Comprehensive event logging
- ✅ View functions for frontend integration

## Contract Addresses

- **FAN Token**: `0x1F0a316ba43224D87d7024C312Ff52E1c8A2CED9`
- **LeaderboardRewards**: (Deploy to get address)

## Prerequisites

1. Node.js (v16 or higher)
2. npm or yarn
3. A wallet with CHZ tokens on Chiliz Spicy Testnet
4. Your wallet's private key

## Installation

1. Navigate to the contracts directory:
```bash
cd contracts
```

2. Install dependencies:
```bash
npm install
```

3. Create environment file:
```bash
cp env.example .env
```

4. Edit `.env` and add your private key:
```
PRIVATE_KEY=your_private_key_here
```

## Deployment

1. Compile the contract:
```bash
npm run compile
```

2. Deploy to Chiliz Spicy Testnet:
```bash
npm run deploy
```

3. The deployment script will output the contract address and save it to `deployment-info.json`

## Contract Functions

### Admin Functions (Only Owner)

#### `setWinners(address[] calldata _winners)`
Set the list of winner addresses (max 10).

#### `setRewardAmount(uint256 _rewardAmount)`
Set the reward amount per winner in FAN tokens (with 18 decimals).

#### `withdrawTokens(address _to, uint256 _amount)`
Withdraw remaining FAN tokens from the contract.

### Winner Functions

#### `claimReward()`
Allow winners to claim their reward (can only be called once per winner).

### View Functions

#### `getWinners()`
Get the list of all winner addresses.

#### `getWinnerCount()`
Get the number of winners.

#### `rewardPerWinner()`
Get the reward amount per winner.

#### `isWinner(address _address)`
Check if an address is a winner.

#### `hasClaimed(address _winner)`
Check if a winner has already claimed their reward.

#### `getTotalRewardAmount()`
Get the total reward amount needed for all winners.

#### `getUnclaimedRewards()`
Get the remaining unclaimed rewards.

#### `getContractBalance()`
Get the contract's FAN token balance.

## Usage Workflow

### 1. Deploy Contract
```bash
npm run deploy
```

### 2. Fund the Contract
Transfer FAN tokens to the contract address:
```solidity
// Using FAN token contract
fanToken.transfer(leaderboardRewardsAddress, totalRewardAmount);
```

### 3. Set Reward Amount
```solidity
// Set reward per winner (e.g., 100 FAN tokens)
leaderboardRewards.setRewardAmount(ethers.utils.parseEther("100"));
```

### 4. Set Winners
```solidity
// Set the top 10 winners
address[] memory winners = [
    0x1234..., // 1st place
    0x5678..., // 2nd place
    // ... up to 10 addresses
];
leaderboardRewards.setWinners(winners);
```

### 5. Winners Claim Rewards
```solidity
// Each winner calls this function
leaderboardRewards.claimReward();
```

## Frontend Integration

The contract includes a TypeScript integration file at `frontend/lib/contracts.ts` with:

- Contract interaction classes
- Web3 provider setup
- Utility functions for token formatting
- Complete ABI definitions

### Example Frontend Usage

```typescript
import { LeaderboardRewardsContract, connectWallet } from '../lib/contracts';

// Connect wallet
const signer = await connectWallet();
const provider = signer.provider;

// Initialize contract
const contract = new LeaderboardRewardsContract(
  contractAddress,
  signer,
  provider
);

// Get winners
const winners = await contract.getWinners();

// Check if user is winner
const isWinner = await contract.isWinner(userAddress);

// Claim reward
if (isWinner && !await contract.hasClaimed(userAddress)) {
  const tx = await contract.claimReward();
  await tx.wait();
}
```

## Security Features

- **Ownable**: Only contract owner can set winners and reward amounts
- **ReentrancyGuard**: Prevents reentrancy attacks during reward claiming
- **Input Validation**: Validates addresses and amounts
- **Double Claim Prevention**: Tracks claimed status per winner
- **Balance Checks**: Ensures sufficient token balance before transfers

## Events

The contract emits events for important actions:

- `WinnersSet(address[] winners)`: When winners are set
- `RewardClaimed(address winner, uint256 amount)`: When a reward is claimed
- `RewardAmountUpdated(uint256 newAmount)`: When reward amount is updated
- `TokensWithdrawn(address to, uint256 amount)`: When tokens are withdrawn

## Testing

Run tests to verify contract functionality:
```bash
npm test
```

## Network Configuration

- **Network**: Chiliz Spicy Testnet
- **Chain ID**: 88882
- **RPC URL**: https://spicy-rpc.chiliz.com
- **Explorer**: https://explorer.chiliz.com

## Gas Optimization

The contract is optimized for gas efficiency:
- Uses `calldata` for function parameters
- Efficient storage patterns
- Minimal external calls
- Optimized loops and conditionals

## License

MIT License - see LICENSE file for details. 