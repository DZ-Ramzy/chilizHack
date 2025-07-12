# 🚀 Guide de Déploiement du Système de Staking

## 📋 **Vue d'ensemble**

Ce guide vous accompagne dans le déploiement et la configuration du système de staking avec niveaux et APY dynamique basé sur les quêtes.

## 🏗️ **Architecture du Système**

### **Smart Contract StakingRewards**
- **Fonctionnalités principales :**
  - Staking/Unstaking de tokens FAN
  - Système de niveaux (0-10) basé sur les quêtes complétées
  - APY dynamique selon le niveau (5% à 50%)
  - Récompenses en temps réel
  - Gestion des quêtes par l'admin

### **Niveaux et APY**
| Niveau | Nom | Quêtes Requises | APY |
|--------|-----|----------------|-----|
| 0 | Débutant | 0 | 5% |
| 1 | Novice | 5 | 8% |
| 2 | Amateur | 15 | 12% |
| 3 | Passionné | 30 | 16% |
| 4 | Expert | 50 | 20% |
| 5 | Maître | 75 | 25% |
| 6 | Légende | 100 | 30% |
| 7 | Champion | 150 | 35% |
| 8 | Héros | 200 | 40% |
| 9 | Dieu | 300 | 45% |
| 10 | Immortel | 500 | 50% |

## 🚀 **Étapes de Déploiement**

### **1. Préparation de l'Environnement**

```bash
# Naviguer vers le dossier contracts
cd contracts

# Installer les dépendances
npm install

# Vérifier la configuration Hardhat
npx hardhat compile
```

### **2. Configuration des Variables d'Environnement**

Créer un fichier `.env` dans le dossier `contracts/` :

```env
PRIVATE_KEY=votre_clé_privée_ici
CHILIZ_SPICY_RPC_URL=https://spicy-rpc.chiliz.com
ETHERSCAN_API_KEY=votre_clé_etherscan_ici
```

### **3. Déploiement du Contrat**

```bash
# Déployer le contrat StakingRewards
npx hardhat run scripts/deploy-staking.js --network chilizSpicy

# Le script affichera l'adresse du contrat déployé
# Exemple : StakingRewards deployed to: 0x...
```

### **4. Financement du Contrat**

```bash
# Mettre à jour l'adresse dans le script
# Éditer scripts/fund-staking.js et remplacer STAKING_REWARDS_ADDRESS

# Financer le contrat avec des tokens FAN
npx hardhat run scripts/fund-staking.js --network chilizSpicy
```

### **5. Test du Contrat**

```bash
# Mettre à jour l'adresse dans le script
# Éditer scripts/test-staking.js et remplacer STAKING_REWARDS_ADDRESS

# Tester les fonctionnalités
npx hardhat run scripts/test-staking.js --network chilizSpicy
```

## 🔧 **Configuration Frontend**

### **1. Mise à Jour des Adresses**

Après le déploiement, mettre à jour les adresses dans le frontend :

```typescript
// frontend/hooks/useStakingRewards.ts
const STAKING_REWARDS_ADDRESS = "VOTRE_ADRESSE_CONTRAT_STAKING_DEPLOYEE";
```

### **2. Installation des Dépendances**

```bash
# Naviguer vers le dossier frontend
cd frontend

# Installer les dépendances
npm install

# Démarrer le serveur de développement
npm run dev
```

## 🎮 **Utilisation du Système**

### **Pour les Utilisateurs**

1. **Connexion Wallet :** Connectez votre wallet (MetaMask, etc.)
2. **Staking :** Entrez le montant de FAN à staker et cliquez sur "Stake"
3. **Suivi des Récompenses :** Consultez vos récompenses en attente
4. **Claim :** Réclamez vos récompenses quand vous le souhaitez
5. **Unstaking :** Retirez vos tokens stakés si nécessaire

### **Pour l'Administrateur**

1. **Marquer les Quêtes :** Utilisez `completeQuest()` pour marquer une quête comme complétée
2. **Marquer Plusieurs Quêtes :** Utilisez `completeMultipleQuests()` pour plusieurs quêtes
3. **Gérer les Récompenses :** Ajustez le taux de récompense avec `setRewardPerSecond()`
4. **Modifier les APY :** Utilisez `updateLevelAPY()` pour ajuster les taux par niveau

## 📊 **Fonctions Administrateur**

### **Marquer une Quête Complétée**
```javascript
await stakingContract.completeQuest(userAddress);
```

### **Marquer Plusieurs Quêtes**
```javascript
await stakingContract.completeMultipleQuests(userAddress, 5); // 5 quêtes
```

### **Définir le Taux de Récompense**
```javascript
// 1 FAN par jour = 1/86400 FAN par seconde
const rewardPerSecond = ethers.utils.parseEther("1").div(86400);
await stakingContract.setRewardPerSecond(rewardPerSecond);
```

### **Modifier l'APY d'un Niveau**
```javascript
// Modifier l'APY du niveau 5 à 30%
await stakingContract.updateLevelAPY(5, 3000); // 3000 = 30%
```

## 🔍 **Vérification et Monitoring**

### **Informations Utilisateur**
```javascript
const userStake = await stakingContract.getUserStake(userAddress);
console.log(`Niveau: ${userStake.userLevel}`);
console.log(`APY: ${userStake.apy}%`);
console.log(`Tokens Stakés: ${userStake.stakedAmount}`);
console.log(`Récompenses en Attente: ${userStake.pendingRewards}`);
```

### **Informations Globales**
```javascript
const totalInfo = await stakingContract.getTotalInfo();
console.log(`Total Staké: ${totalInfo._totalStaked}`);
console.log(`Récompenses Distribuées: ${totalInfo._totalRewardsDistributed}`);
console.log(`Balance du Contrat: ${totalInfo._contractBalance}`);
```

## 🛡️ **Sécurité et Bonnes Pratiques**

### **Sécurité du Contrat**
- ✅ Utilisation d'OpenZeppelin pour les contrats de base
- ✅ Protection contre les attaques de réentrance
- ✅ Gestion des permissions avec Ownable
- ✅ Validation des entrées utilisateur

### **Bonnes Pratiques**
- 🔒 Gardez votre clé privée en sécurité
- 📝 Documentez toutes les modifications
- 🧪 Testez toujours sur le testnet avant le mainnet
- 📊 Surveillez les événements du contrat
- 💰 Maintenez un solde suffisant pour les récompenses

## 🚨 **Dépannage**

### **Erreurs Courantes**

1. **"Insufficient balance"**
   - Vérifiez que l'utilisateur a assez de tokens FAN
   - Vérifiez l'allowance du contrat

2. **"Transfer failed"**
   - Vérifiez le solde du contrat
   - Vérifiez les permissions

3. **"No rewards to claim"**
   - L'utilisateur n'a pas de récompenses en attente
   - Vérifiez que l'utilisateur staké des tokens

### **Support**

Pour toute question ou problème :
1. Vérifiez les logs de transaction
2. Consultez les événements du contrat
3. Testez avec de petits montants d'abord

## 🎯 **Prochaines Étapes**

1. **Intégration avec le Backend :** Connecter le système de quêtes existant
2. **Analytics :** Ajouter des métriques et tableaux de bord
3. **Notifications :** Système de notifications pour les récompenses
4. **Gamification :** Badges et achievements supplémentaires
5. **Mobile App :** Application mobile dédiée

---

**🎉 Félicitations ! Votre système de staking est maintenant opérationnel !** 