"use client"

import Link from 'next/link';
import { usePrivy } from '@privy-io/react-auth';

export default function HomePage() {
  const { authenticated, login } = usePrivy();

  return (
    <div 
      className="min-h-screen w-full relative overflow-hidden"
      style={{
        backgroundImage: 'url(/bg.jpg)',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
      }}
    >
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" />
      
      <div className="relative z-10 min-h-screen flex items-center justify-center px-4">
        <div className="max-w-5xl w-full">
          <div className="bg-black/40 backdrop-blur-md rounded-3xl p-8 md:p-12 border border-white/10">
            <div className="flex flex-col items-center text-center mb-12">
              <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 bg-gradient-to-r from-red-500 to-orange-500 bg-clip-text text-transparent">
                Chiliz Quest
              </h1>
              <p className="text-xl md:text-2xl text-white/90 max-w-2xl">
                Embark on an epic journey through the Chiliz ecosystem
              </p>
            </div>

            <div className="flex justify-center mb-16">
              {authenticated ? (
                <Link 
                  href="/onboarding"
                  className="relative inline-flex items-center justify-center px-8 py-4 rounded-full bg-gradient-to-r from-red-500 to-orange-500 text-white font-bold text-lg transition-all duration-300 hover:scale-105"
                >
                  Start Your Quest
                </Link>
              ) : (
                <button
                  onClick={login}
                  className="relative inline-flex items-center justify-center px-8 py-4 rounded-full bg-gradient-to-r from-red-500 to-orange-500 text-white font-bold text-lg transition-all duration-300 hover:scale-105"
                >
                  Connect Wallet to Start
                </button>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-black/30 border border-white/10 p-8 rounded-2xl transition-all duration-300 hover:bg-black/40">
                <h3 className="text-2xl font-semibold text-white mb-3">Complete Missions</h3>
                <p className="text-white/80">Take on exciting challenges and prove your dedication to the Chiliz community</p>
              </div>
              
              <div className="bg-black/30 border border-white/10 p-8 rounded-2xl transition-all duration-300 hover:bg-black/40">
                <h3 className="text-2xl font-semibold text-white mb-3">Earn Rewards</h3>
                <p className="text-white/80">Get exclusive rewards and recognition for your achievements in the quest</p>
              </div>
              
              <div className="bg-black/30 border border-white/10 p-8 rounded-2xl transition-all duration-300 hover:bg-black/40">
                <h3 className="text-2xl font-semibold text-white mb-3">Join Community</h3>
                <p className="text-white/80">Connect with fellow enthusiasts and be part of the growing Chiliz ecosystem</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
