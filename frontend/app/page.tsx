"use client"

import Link from 'next/link';
import { usePrivy } from '@privy-io/react-auth';
import Image from 'next/image';

export default function HomePage() {
  const { authenticated, login } = usePrivy();

  return (
    <div className="min-h-screen w-full relative bg-white">
      {/* Background Pattern */}
      <div className="absolute inset-0 z-0">
        <div className="absolute inset-0" style={{
          backgroundImage: 'radial-gradient(#E2E2FF 1px, transparent 1px)',
          backgroundSize: '24px 24px'
        }}></div>
      </div>
      {/* Navigation */}
      <nav className="relative z-10 px-6 py-6">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="text-xl font-medium text-gray-900">Chiliz Quest</div>
          <div className="flex items-center gap-8">
            {authenticated ? (
              <Link 
                href="/dashboard"
                className="px-4 py-2 rounded-lg bg-black text-white hover:bg-gray-800 transition-colors"
              >
                Dashboard
              </Link>
            ) : (
              <button
                onClick={login}
                className="px-4 py-2 rounded-lg bg-black text-white hover:bg-gray-800 transition-colors"
              >
                Connect Wallet
              </button>
            )}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="relative">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex">
            {/* Left Content */}
            <div className="w-1/2 pt-20 pr-20 min-h-[calc(100vh-200px)] flex flex-col justify-center">
              <div className="mb-2 inline-block">
                <span className="text-sm font-medium bg-purple-100 text-purple-800 px-3 py-1 rounded-full">
                  Onchain Rewards
                </span>
              </div>
              
              <h1 className="text-[64px] leading-[1.1] font-light text-gray-900 mb-6">
                Earn <span className="font-bold">rewards</span> with your <span className="font-bold">favorite teams</span>
              </h1>

              <p className="text-xl text-gray-600 mb-12">
                Complete quests, earn rewards, and join a community of passionate fans in the Chiliz ecosystem.
              </p>

              <div className="flex gap-4">
                <div className="flex-1">
                  {authenticated ? (
                    <Link
                      href="/main"
                      className="inline-flex items-center text-sm font-medium text-gray-900 hover:text-gray-700 bg-black text-white px-4 py-2 rounded-lg"
                    >
                      Get Started <span className="ml-2">→</span>
                    </Link>
                  ) : (
                    <button
                      onClick={login}
                      className="inline-flex items-center text-sm font-medium text-gray-900 hover:text-gray-700 bg-black text-white px-4 py-2 rounded-lg"
                    >
                      Get Started <span className="ml-2">→</span>
                    </button>
                  )}
                </div>
              </div>
            </div>

            {/* Right Content - Purple Rectangle */}
            <div className="w-1/2 relative">
              <div className="absolute inset-0 bg-[#F0F0FF] rounded-l-3xl">
                {/* Add some subtle decoration */}
                <img src="/scan.jpeg" alt="scan" className="w-full h-full object-cover" />
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
