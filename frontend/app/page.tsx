"use client"

import Link from 'next/link';
import { usePrivy } from '@privy-io/react-auth';
import Navbar from '../components/Navbar';
import Reviews from '../components/Reviews';
import { Instagram } from 'lucide-react';

export default function HomePage() {
  const { authenticated, login, user } = usePrivy();

  return (
    <div className="min-h-screen w-full relative bg-white">
      {/* Background Pattern */}
      <div className="absolute inset-0 z-0">
        <div className="absolute inset-0" style={{
          backgroundImage: 'radial-gradient(#E2E2FF 1px, transparent 1px)',
          backgroundSize: '24px 24px'
        }}></div>
      </div>
      
      <Navbar />

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
                      href={user?.customMetadata?.xp === 0 ? "/onboarding" : "/main"}
                      className="inline-flex items-center text-sm font-medium text-gray-900 hover:bg-gray-900 hover:text-white bg-black text-white px-4 py-2 rounded-lg"
                    >
                      Get Started <span className="ml-2">→</span>
                    </Link>
                  ) : (
                    <button
                      onClick={login}
                      className="inline-flex items-center text-sm font-medium text-gray-900 hover:bg-gray-900 hover:text-white bg-black text-white px-4 py-2 rounded-lg"
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
                <img src="/scan.jpeg" alt="scan" className="w-full h-full object-cover" />
              </div>
            </div>
          </div>
          <div className="py-32">
            <Reviews />
          </div>
        </div>
        <div className="py-32 overflow-hidden bg-gradient-to-r from-black to-pink-900">
            <div className='max-w-7xl mx-auto flex flex-col gap-4'>
              <p className='text-white text-4xl font-bold'>Make Football Great Again</p>
              <p className='text-white text-xl'>Join the Chiliz ecosystem and earn rewards with your favorite teams</p>
              <Instagram className='w-10 h-10 text-white' />
            </div>
          </div>
      </main>
    </div>
  );
}
