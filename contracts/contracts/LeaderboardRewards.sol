// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title LeaderboardRewards
 * @dev Manages reward distribution for leaderboard winners using FAN tokens
 */
contract LeaderboardRewards is Ownable, ReentrancyGuard {
    IERC20 public immutable fanToken;
    
    // FAN token address on Chiliz Spicy Testnet
    address public constant FAN_TOKEN_ADDRESS = 0x1F0a316ba43224D87d7024C312Ff52E1c8A2CED9;
    
    // Maximum number of winners
    uint256 public constant MAX_WINNERS = 10;
    
    // Reward amount per winner (in FAN tokens with 18 decimals)
    uint256 public rewardPerWinner;
    
    // Array of winner addresses
    address[] public winners;
    
    // Mapping to track if a winner has claimed their reward
    mapping(address => bool) public hasClaimed;
    
    // Events
    event WinnersSet(address[] winners);
    event RewardClaimed(address winner, uint256 amount);
    event RewardAmountUpdated(uint256 newAmount);
    event TokensWithdrawn(address to, uint256 amount);
    
    /**
     * @dev Constructor sets the FAN token address
     */
    constructor() {
        fanToken = IERC20(FAN_TOKEN_ADDRESS);
    }
    
    /**
     * @dev Modifier to ensure only winners can call functions
     */
    modifier onlyWinner() {
        require(isWinner(msg.sender), "LeaderboardRewards: caller is not a winner");
        _;
    }
    
    /**
     * @dev Check if an address is a winner
     * @param _address Address to check
     * @return bool True if address is a winner
     */
    function isWinner(address _address) public view returns (bool) {
        for (uint256 i = 0; i < winners.length; i++) {
            if (winners[i] == _address) {
                return true;
            }
        }
        return false;
    }
    
    /**
     * @dev Set the winners for the leaderboard (only owner)
     * @param _winners Array of winner addresses (max 10)
     */
    function setWinners(address[] calldata _winners) external onlyOwner {
        require(_winners.length <= MAX_WINNERS, "LeaderboardRewards: too many winners");
        require(_winners.length > 0, "LeaderboardRewards: no winners provided");
        
        // Clear previous winners and claimed status
        delete winners;
        
        // Add new winners
        for (uint256 i = 0; i < _winners.length; i++) {
            require(_winners[i] != address(0), "LeaderboardRewards: invalid address");
            winners.push(_winners[i]);
            // Reset claimed status for new winners
            hasClaimed[_winners[i]] = false;
        }
        
        emit WinnersSet(_winners);
    }
    
    /**
     * @dev Set the reward amount per winner (only owner)
     * @param _rewardAmount Amount of FAN tokens per winner (with 18 decimals)
     */
    function setRewardAmount(uint256 _rewardAmount) external onlyOwner {
        require(_rewardAmount > 0, "LeaderboardRewards: reward amount must be greater than 0");
        rewardPerWinner = _rewardAmount;
        emit RewardAmountUpdated(_rewardAmount);
    }
    
    /**
     * @dev Allow winners to claim their reward
     */
    function claimReward() external onlyWinner nonReentrant {
        require(!hasClaimed[msg.sender], "LeaderboardRewards: reward already claimed");
        require(rewardPerWinner > 0, "LeaderboardRewards: reward amount not set");
        
        // Check if contract has enough tokens
        uint256 contractBalance = fanToken.balanceOf(address(this));
        require(contractBalance >= rewardPerWinner, "LeaderboardRewards: insufficient token balance");
        
        // Mark as claimed
        hasClaimed[msg.sender] = true;
        
        // Transfer tokens to winner
        require(fanToken.transfer(msg.sender, rewardPerWinner), "LeaderboardRewards: transfer failed");
        
        emit RewardClaimed(msg.sender, rewardPerWinner);
    }
    
    /**
     * @dev Get the list of all winners
     * @return address[] Array of winner addresses
     */
    function getWinners() external view returns (address[] memory) {
        return winners;
    }
    
    /**
     * @dev Get the number of winners
     * @return uint256 Number of winners
     */
    function getWinnerCount() external view returns (uint256) {
        return winners.length;
    }
    
    /**
     * @dev Check if a specific winner has claimed their reward
     * @param _winner Address of the winner to check
     * @return bool True if winner has claimed
     */
    function getClaimStatus(address _winner) external view returns (bool) {
        return hasClaimed[_winner];
    }
    
    /**
     * @dev Get the total reward amount needed for all winners
     * @return uint256 Total reward amount
     */
    function getTotalRewardAmount() external view returns (uint256) {
        return winners.length * rewardPerWinner;
    }
    
    /**
     * @dev Get the remaining unclaimed rewards
     * @return uint256 Remaining unclaimed rewards
     */
    function getUnclaimedRewards() external view returns (uint256) {
        uint256 claimedCount = 0;
        for (uint256 i = 0; i < winners.length; i++) {
            if (hasClaimed[winners[i]]) {
                claimedCount++;
            }
        }
        return (winners.length - claimedCount) * rewardPerWinner;
    }
    
    /**
     * @dev Allow owner to withdraw remaining FAN tokens (only owner)
     * @param _to Address to send tokens to
     * @param _amount Amount of tokens to withdraw
     */
    function withdrawTokens(address _to, uint256 _amount) external onlyOwner {
        require(_to != address(0), "LeaderboardRewards: invalid recipient");
        require(_amount > 0, "LeaderboardRewards: amount must be greater than 0");
        
        uint256 contractBalance = fanToken.balanceOf(address(this));
        require(contractBalance >= _amount, "LeaderboardRewards: insufficient balance");
        
        require(fanToken.transfer(_to, _amount), "LeaderboardRewards: transfer failed");
        
        emit TokensWithdrawn(_to, _amount);
    }
    
    /**
     * @dev Get contract's FAN token balance
     * @return uint256 Contract's token balance
     */
    function getContractBalance() external view returns (uint256) {
        return fanToken.balanceOf(address(this));
    }
} 