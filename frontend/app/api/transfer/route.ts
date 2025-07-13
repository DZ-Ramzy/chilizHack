import { ethers } from 'ethers';
import { NextResponse } from 'next/server';

// ABI standard ERC20
const minABI = [
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "_to",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "_value",
        "type": "uint256"
      }
    ],
    "name": "transfer",
    "outputs": [
      {
        "internalType": "bool",
        "name": "",
        "type": "bool"
      }
    ],
    "stateMutability": "nonpayable",
    "type": "function"
  }
];

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { privateKey, toAddress } = body;

    if (!privateKey || !toAddress) {
      return NextResponse.json(
        { error: 'Private key and destination address are required' },
        { status: 400 }
      );
    }

    // Connexion au réseau Chiliz Testnet (Spicy)
    const provider = new ethers.JsonRpcProvider('https://spicy-rpc.chiliz.com/');
    
    // Création du wallet avec la private key
    const wallet = new ethers.Wallet(privateKey, provider);
    const walletAddress = await wallet.getAddress();
    
    // Afficher l'adresse du wallet (clé publique)
    console.log('Wallet address (public key):', walletAddress);
    
    // Vérifier le solde de CHZ pour le gas
    const chzBalance = await provider.getBalance(walletAddress);
    console.log('CHZ Balance:', ethers.formatEther(chzBalance), 'CHZ');
    
    // Adresse du token FAN
    const tokenAddress = '0x1F0a316ba43224D87d7024C312Ff52E1c8A2CED9';

    // Vérifier si le contrat existe
    const contractCode = await provider.getCode(tokenAddress);
    console.log('Contract code length:', contractCode.length);
    if (contractCode === '0x') {
      return NextResponse.json(
        { error: 'Token contract not found at the specified address' },
        { status: 400 }
      );
    }
    
    // Création de l'instance du contrat
    const contract = new ethers.Contract(tokenAddress, minABI, wallet);
    
    // Montant à transférer (1 coin)
    const amount = ethers.parseUnits('1', 18); // Les tokens ERC20 utilisent généralement 18 décimales

    try {
      // Préparer la transaction
      console.log('Estimating gas for transfer...');
      const gasLimit = await contract.transfer.estimateGas(toAddress, amount, {
        from: walletAddress
      });
      
      console.log('Estimated gas limit:', gasLimit.toString());
      
      // Envoi de la transaction avec gas limit explicite
      const tx = await contract.transfer(toAddress, amount, {
        gasLimit: gasLimit * BigInt(12) / BigInt(10) // +20% pour la sécurité
      });
      
      console.log('Transaction sent:', tx.hash);
      
      // Attente de la confirmation
      const receipt = await tx.wait();
      
      return NextResponse.json({
        success: true,
        walletAddress: walletAddress,
        transactionHash: receipt.hash,
        blockNumber: receipt.blockNumber
      });
    } catch (error: unknown) {
      console.error('Operation error:', error);
      throw error; // Propager l'erreur pour la gestion globale
    }
    
  } catch (error: unknown) {
    console.error('Transaction error:', error);
    
    // Gestion plus détaillée des erreurs
    let errorMessage = 'Failed to process transaction';
    if (error && typeof error === 'object' && 'code' in error) {
      if (error.code === 'CALL_EXCEPTION' && 'reason' in error) {
        errorMessage = 'Contract call failed: ' + (error.reason || 'Unknown reason');
      } else if (error.code === 'INSUFFICIENT_FUNDS') {
        errorMessage = 'Insufficient CHZ for gas';
      }
    }
    
    return NextResponse.json(
      { error: errorMessage },
      { status: 500 }
    );
  }
} 