// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";

/**
 * @title StakingRewards
 * @dev Smart contract pour le staking avec système de niveaux et APY dynamique
 */
contract StakingRewards is Ownable, ReentrancyGuard {
    using SafeMath for uint256;

    IERC20 public immutable fanToken;
    
    // FAN token address on Chiliz Spicy Testnet
    address public constant FAN_TOKEN_ADDRESS = 0x1F0a316ba43224D87d7024C312Ff52E1c8A2CED9;
    
    // Structure pour les informations de staking d'un utilisateur
    struct UserStake {
        uint256 stakedAmount;        // Montant staké
        uint256 rewardDebt;          // Dette de récompense (pour calcul précis)
        uint256 lastUpdateTime;      // Dernière mise à jour
        uint256 userLevel;           // Niveau de l'utilisateur (0-10)
        uint256 questsCompleted;     // Nombre de quêtes complétées
        bool isStaking;              // Si l'utilisateur staké actuellement
    }
    
    // Structure pour les niveaux
    struct Level {
        uint256 minQuests;           // Quêtes minimum pour ce niveau
        uint256 apy;                 // APY en base points (100 = 1%)
        string name;                 // Nom du niveau
    }
    
    // Variables globales
    uint256 public totalStaked;                      // Total staké
    uint256 public totalRewardsDistributed;          // Total des récompenses distribuées
    uint256 public rewardPerSecond;                  // Récompenses par seconde
    uint256 public lastUpdateTime;                   // Dernière mise à jour globale
    uint256 public accRewardPerShare;                // Récompenses accumulées par part
    
    // Mapping des utilisateurs
    mapping(address => UserStake) public userStakes;
    
    // Mapping des niveaux
    mapping(uint256 => Level) public levels;
    uint256 public totalLevels;
    
    // Événements
    event Staked(address indexed user, uint256 amount, uint256 level);
    event Unstaked(address indexed user, uint256 amount);
    event RewardsClaimed(address indexed user, uint256 amount);
    event LevelUp(address indexed user, uint256 oldLevel, uint256 newLevel);
    event QuestCompleted(address indexed user, uint256 questsCompleted, uint256 newLevel);
    event APYUpdated(uint256 level, uint256 newAPY);
    
    /**
     * @dev Constructor - initialise les niveaux
     */
    constructor() {
        fanToken = IERC20(FAN_TOKEN_ADDRESS);
        
        // Initialiser les niveaux
        _initializeLevels();
        
        lastUpdateTime = block.timestamp;
    }
    
    /**
     * @dev Initialise les niveaux avec leurs APY
     */
    function _initializeLevels() internal {
        // Level 0: Beginner (0 quests) - 5% APY
        levels[0] = Level(0, 500, "Beginner");
        
        // Level 1: Novice (5 quests) - 8% APY
        levels[1] = Level(5, 800, "Novice");
        
        // Level 2: Amateur (15 quests) - 12% APY
        levels[2] = Level(15, 1200, "Amateur");
        
        // Level 3: Enthusiast (30 quests) - 16% APY
        levels[3] = Level(30, 1600, "Enthusiast");
        
        // Level 4: Expert (50 quests) - 20% APY
        levels[4] = Level(50, 2000, "Expert");
        
        // Level 5: Master (75 quests) - 25% APY
        levels[5] = Level(75, 2500, "Master");
        
        // Level 6: Legend (100 quests) - 30% APY
        levels[6] = Level(100, 3000, "Legend");
        
        // Level 7: Champion (150 quests) - 35% APY
        levels[7] = Level(150, 3500, "Champion");
        
        // Level 8: Hero (200 quests) - 40% APY
        levels[8] = Level(200, 4000, "Hero");
        
        // Level 9: God (300 quests) - 45% APY
        levels[9] = Level(300, 4500, "God");
        
        // Level 10: Immortal (500 quests) - 50% APY
        levels[10] = Level(500, 5000, "Immortal");
        
        totalLevels = 11;
    }
    
    /**
     * @dev Met à jour les récompenses globales
     */
    function _updateRewards() internal {
        if (block.timestamp <= lastUpdateTime) return;
        
        if (totalStaked > 0) {
            uint256 timePassed = block.timestamp.sub(lastUpdateTime);
            uint256 rewards = timePassed.mul(rewardPerSecond);
            accRewardPerShare = accRewardPerShare.add(rewards.mul(1e18).div(totalStaked));
        }
        
        lastUpdateTime = block.timestamp;
    }
    
    /**
     * @dev Met à jour les récompenses d'un utilisateur
     */
    function _updateUserRewards(address user) internal {
        UserStake storage userStake = userStakes[user];
        
        if (userStake.stakedAmount > 0) {
            uint256 pending = userStake.stakedAmount.mul(accRewardPerShare).div(1e18).sub(userStake.rewardDebt);
            userStake.rewardDebt = userStake.stakedAmount.mul(accRewardPerShare).div(1e18);
        }
        
        userStake.lastUpdateTime = block.timestamp;
    }
    
    /**
     * @dev Calcule le niveau d'un utilisateur basé sur ses quêtes
     */
    function _calculateUserLevel(uint256 questsCompleted) internal view returns (uint256) {
        for (uint256 i = totalLevels - 1; i >= 0; i--) {
            if (questsCompleted >= levels[i].minQuests) {
                return i;
            }
        }
        return 0;
    }
    
    /**
     * @dev Stake des tokens FAN
     */
    function stake(uint256 amount) external nonReentrant {
        require(amount > 0, "StakingRewards: amount must be greater than 0");
        require(fanToken.balanceOf(msg.sender) >= amount, "StakingRewards: insufficient balance");
        
        _updateRewards();
        _updateUserRewards(msg.sender);
        
        UserStake storage userStake = userStakes[msg.sender];
        
        // Calculer le niveau actuel
        uint256 currentLevel = _calculateUserLevel(userStake.questsCompleted);
        
        // Mettre à jour les informations de staking
        if (userStake.stakedAmount > 0) {
            userStake.stakedAmount = userStake.stakedAmount.add(amount);
        } else {
            userStake.stakedAmount = amount;
            userStake.userLevel = currentLevel;
            userStake.isStaking = true;
        }
        
        totalStaked = totalStaked.add(amount);
        
        // Transférer les tokens
        require(fanToken.transferFrom(msg.sender, address(this), amount), "StakingRewards: transfer failed");
        
        emit Staked(msg.sender, amount, currentLevel);
    }
    
    /**
     * @dev Unstake des tokens FAN
     */
    function unstake(uint256 amount) external nonReentrant {
        UserStake storage userStake = userStakes[msg.sender];
        require(userStake.stakedAmount >= amount, "StakingRewards: insufficient staked amount");
        
        _updateRewards();
        _updateUserRewards(msg.sender);
        
        userStake.stakedAmount = userStake.stakedAmount.sub(amount);
        totalStaked = totalStaked.sub(amount);
        
        if (userStake.stakedAmount == 0) {
            userStake.isStaking = false;
        }
        
        // Transférer les tokens
        require(fanToken.transfer(msg.sender, amount), "StakingRewards: transfer failed");
        
        emit Unstaked(msg.sender, amount);
    }
    
    /**
     * @dev Réclamer les récompenses
     */
    function claimRewards() external nonReentrant {
        _updateRewards();
        _updateUserRewards(msg.sender);
        
        UserStake storage userStake = userStakes[msg.sender];
        uint256 pending = userStake.stakedAmount.mul(accRewardPerShare).div(1e18).sub(userStake.rewardDebt);
        
        require(pending > 0, "StakingRewards: no rewards to claim");
        
        userStake.rewardDebt = userStake.stakedAmount.mul(accRewardPerShare).div(1e18);
        totalRewardsDistributed = totalRewardsDistributed.add(pending);
        
        // Transférer les récompenses
        require(fanToken.transfer(msg.sender, pending), "StakingRewards: transfer failed");
        
        emit RewardsClaimed(msg.sender, pending);
    }
    
    /**
     * @dev Marquer une quête comme complétée (seulement owner)
     */
    function completeQuest(address user) external onlyOwner {
        UserStake storage userStake = userStakes[user];
        uint256 oldLevel = userStake.userLevel;
        
        userStake.questsCompleted = userStake.questsCompleted.add(1);
        userStake.userLevel = _calculateUserLevel(userStake.questsCompleted);
        
        emit QuestCompleted(user, userStake.questsCompleted, userStake.userLevel);
        
        if (userStake.userLevel > oldLevel) {
            emit LevelUp(user, oldLevel, userStake.userLevel);
        }
    }
    
    /**
     * @dev Marquer plusieurs quêtes comme complétées (seulement owner)
     */
    function completeMultipleQuests(address user, uint256 questCount) external onlyOwner {
        UserStake storage userStake = userStakes[user];
        uint256 oldLevel = userStake.userLevel;
        
        userStake.questsCompleted = userStake.questsCompleted.add(questCount);
        userStake.userLevel = _calculateUserLevel(userStake.questsCompleted);
        
        emit QuestCompleted(user, userStake.questsCompleted, userStake.userLevel);
        
        if (userStake.userLevel > oldLevel) {
            emit LevelUp(user, oldLevel, userStake.userLevel);
        }
    }
    
    /**
     * @dev Définir le taux de récompense par seconde (seulement owner)
     */
    function setRewardPerSecond(uint256 _rewardPerSecond) external onlyOwner {
        _updateRewards();
        rewardPerSecond = _rewardPerSecond;
    }
    
    /**
     * @dev Mettre à jour l'APY d'un niveau (seulement owner)
     */
    function updateLevelAPY(uint256 level, uint256 newAPY) external onlyOwner {
        require(level < totalLevels, "StakingRewards: invalid level");
        levels[level].apy = newAPY;
        emit APYUpdated(level, newAPY);
    }
    
    /**
     * @dev Ajouter des tokens de récompense au contrat (seulement owner)
     */
    function addRewardTokens(uint256 amount) external onlyOwner {
        require(fanToken.transferFrom(msg.sender, address(this), amount), "StakingRewards: transfer failed");
    }
    
    /**
     * @dev Retirer des tokens du contrat (seulement owner)
     */
    function withdrawTokens(address to, uint256 amount) external onlyOwner {
        require(fanToken.transfer(to, amount), "StakingRewards: transfer failed");
    }
    
    // Fonctions de vue
    
    /**
     * @dev Obtenir les informations de staking d'un utilisateur
     */
    function getUserStake(address user) external view returns (
        uint256 stakedAmount,
        uint256 pendingRewards,
        uint256 userLevel,
        uint256 questsCompleted,
        bool isStaking,
        string memory levelName
    ) {
        UserStake storage userStake = userStakes[user];
        
        uint256 _accRewardPerShare = accRewardPerShare;
        if (block.timestamp > lastUpdateTime && totalStaked > 0) {
            uint256 timePassed = block.timestamp.sub(lastUpdateTime);
            uint256 rewards = timePassed.mul(rewardPerSecond);
            _accRewardPerShare = _accRewardPerShare.add(rewards.mul(1e18).div(totalStaked));
        }
        
        uint256 pending = 0;
        if (userStake.stakedAmount > 0) {
            pending = userStake.stakedAmount.mul(_accRewardPerShare).div(1e18).sub(userStake.rewardDebt);
        }
        
        return (
            userStake.stakedAmount,
            pending,
            userStake.userLevel,
            userStake.questsCompleted,
            userStake.isStaking,
            levels[userStake.userLevel].name
        );
    }
    
    /**
     * @dev Obtenir les informations d'un niveau
     */
    function getLevelInfo(uint256 level) external view returns (
        uint256 minQuests,
        uint256 apy,
        string memory name
    ) {
        require(level < totalLevels, "StakingRewards: invalid level");
        Level storage levelInfo = levels[level];
        return (levelInfo.minQuests, levelInfo.apy, levelInfo.name);
    }
    
    /**
     * @dev Obtenir l'APY actuel d'un utilisateur
     */
    function getUserAPY(address user) external view returns (uint256) {
        UserStake storage userStake = userStakes[user];
        return levels[userStake.userLevel].apy;
    }
    
    /**
     * @dev Obtenir le total des informations
     */
    function getTotalInfo() external view returns (
        uint256 _totalStaked,
        uint256 _totalRewardsDistributed,
        uint256 _rewardPerSecond,
        uint256 _contractBalance
    ) {
        return (
            totalStaked,
            totalRewardsDistributed,
            rewardPerSecond,
            fanToken.balanceOf(address(this))
        );
    }
} 