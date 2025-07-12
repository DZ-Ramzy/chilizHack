# 🧪 Guide de Test - LeaderboardRewards avec FAN Token

## 📋 Informations du Token FAN

- **Adresse du Token FAN :** `0x1F0a316ba43224D87d7024C312Ff52E1c8A2CED9`
- **Réseau :** Chiliz Spicy Testnet
- **Chain ID :** 88882
- **Décimales :** 18

## 🚀 Étapes de Test

### **Étape 1: Préparation**

1. **Installer les dépendances :**
```bash
cd contracts
npm install
```

2. **Configurer l'environnement :**
```bash
cp env.example .env
# Éditez .env et ajoutez votre clé privée
```

### **Étape 2: Déployer le Contrat**

```bash
npm run deploy
```

**Important :** Notez l'adresse du contrat déployé !

### **Étape 3: Mettre à Jour les Adresses**

Après le déploiement, mettez à jour l'adresse dans :

1. **`contracts/scripts/test-contract.js`** (ligne 8)
2. **`contracts/scripts/fund-contract.js`** (ligne 8)
3. **`frontend/lib/contracts.ts`** (ligne 35)

Remplacez `"VOTRE_ADRESSE_CONTRAT_ICI"` par l'adresse réelle.

### **Étape 4: Transférer des Tokens FAN**

```bash
npm run fund-contract
```

Ce script transfère 1000 FAN tokens au contrat pour les tests.

### **Étape 5: Tester les Fonctionnalités**

```bash
npm run test-contract
```

## 📊 Tests Effectués

Le script `test-contract.js` teste :

1. ✅ **Configuration des récompenses** (50 FAN par gagnant)
2. ✅ **Définition des gagnants** (3 adresses de test)
3. ✅ **Vérification du statut gagnant**
4. ✅ **Calcul du montant total des récompenses**
5. ✅ **Réclamation de récompense** par un gagnant
6. ✅ **Vérification du statut de réclamation**
7. ✅ **Prévention de double réclamation**
8. ✅ **Calcul des récompenses non réclamées**
9. ✅ **Prévention de réclamation par des non-gagnants**

## 🔧 Configuration MetaMask

### Ajouter le Réseau Chiliz Spicy Testnet :

- **Nom :** Chiliz Spicy Testnet
- **RPC URL :** https://spicy-rpc.chiliz.com
- **Chain ID :** 88882
- **Symbole :** CHZ
- **Explorer :** https://explorer.chiliz.com

### Ajouter le Token FAN :

- **Adresse du Contrat :** `0x1F0a316ba43224D87d7024C312Ff52E1c8A2CED9`
- **Symbole :** FAN
- **Décimales :** 18

## 🎯 Test Manuel avec MetaMask

### **1. Vérifier le Solde FAN**

1. Connectez MetaMask au réseau Chiliz Spicy Testnet
2. Ajoutez le token FAN
3. Vérifiez votre solde de tokens FAN

### **2. Tester la Réclamation**

1. Assurez-vous d'être dans la liste des gagnants
2. Connectez votre wallet au frontend
3. Appelez la fonction `claimReward()`
4. Confirmez la transaction dans MetaMask

### **3. Vérifier les Résultats**

1. Vérifiez votre nouveau solde FAN
2. Vérifiez le statut de réclamation sur le contrat
3. Vérifiez les événements émis

## 📝 Scripts Disponibles

```bash
# Déployer le contrat
npm run deploy

# Transférer des tokens FAN au contrat
npm run fund-contract

# Tester toutes les fonctionnalités
npm run test-contract

# Tests unitaires
npm test
```

## 🔍 Vérification sur l'Explorateur

1. Allez sur https://explorer.chiliz.com
2. Recherchez l'adresse de votre contrat
3. Vérifiez les transactions et événements
4. Vérifiez le solde de tokens FAN du contrat

## ⚠️ Points d'Attention

1. **Assurez-vous d'avoir suffisamment de CHZ** pour les frais de gas
2. **Vérifiez votre solde de tokens FAN** avant les tests
3. **Notez l'adresse du contrat** après le déploiement
4. **Testez d'abord avec de petits montants**

## 🆘 Dépannage

### Erreur "Insufficient Balance"
- Vérifiez votre solde de tokens FAN
- Vérifiez votre solde de CHZ pour les frais

### Erreur "Not a Winner"
- Vérifiez que votre adresse est dans la liste des gagnants
- Vérifiez que les gagnants ont été correctement définis

### Erreur "Already Claimed"
- Vérifiez le statut de réclamation de votre adresse
- Chaque gagnant ne peut réclamer qu'une seule fois

## 📞 Support

Si vous rencontrez des problèmes :
1. Vérifiez les logs de transaction
2. Vérifiez les événements émis
3. Vérifiez les balances des comptes
4. Consultez l'explorateur Chiliz 