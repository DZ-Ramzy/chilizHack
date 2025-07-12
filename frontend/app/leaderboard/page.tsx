"use client"

import React from 'react';
import { usePrivy } from '@privy-io/react-auth';
import Navbar from '../../components/Navbar';

type LeaderboardEntry = {
  rank: number;
  address: string;
  points: number;
  completedMissions: number;
};

const leaderboardData: LeaderboardEntry[] = [
  { rank: 1, address: "0x1234...5678", points: 1500, completedMissions: 12 },
  { rank: 2, address: "0x8765...4321", points: 1200, completedMissions: 10 },
  { rank: 3, address: "0x9876...1234", points: 1000, completedMissions: 8 },
  { rank: 4, address: "0x4567...8901", points: 800, completedMissions: 7 },
  { rank: 5, address: "0x2345...6789", points: 600, completedMissions: 5 },
];

export default function LeaderboardPage() {
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
      <main className="relative z-10 max-w-7xl mx-auto px-6 py-12">
        <div className="mb-2 inline-block">
          <span className="text-sm font-medium bg-purple-100 text-purple-800 px-3 py-1 rounded-full">
            Top Players
          </span>
        </div>
        
        <h1 className="text-5xl font-light text-gray-900 mb-8">
          <span className="font-bold">Leaderboard</span> Rankings
        </h1>

        <div className="bg-white shadow-lg rounded-2xl border border-gray-100">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-50">
                  <th className="py-4 px-6 text-left text-sm font-medium text-gray-500">Rank</th>
                  <th className="py-4 px-6 text-left text-sm font-medium text-gray-500">Address</th>
                  <th className="py-4 px-6 text-right text-sm font-medium text-gray-500">Points</th>
                  <th className="py-4 px-6 text-right text-sm font-medium text-gray-500">Missions</th>
                </tr>
              </thead>
              <tbody>
                {leaderboardData.map((entry) => (
                  <tr 
                    key={entry.address}
                    className="border-t border-gray-100 hover:bg-gray-50 transition-colors"
                  >
                    <td className="py-4 px-6">
                      <span className={`
                        inline-flex items-center justify-center w-8 h-8 rounded-full 
                        ${entry.rank === 1 ? 'bg-yellow-100 text-yellow-800' : 
                          entry.rank === 2 ? 'bg-gray-100 text-gray-800' :
                          entry.rank === 3 ? 'bg-amber-100 text-amber-800' : 
                          'bg-purple-100 text-purple-800'}
                        font-bold text-sm
                      `}>
                        {entry.rank}
                      </span>
                    </td>
                    <td className="py-4 px-6 font-mono text-gray-900">{entry.address}</td>
                    <td className="py-4 px-6 text-right font-bold text-purple-600">
                      {entry.points}
                    </td>
                    <td className="py-4 px-6 text-right text-gray-600">{entry.completedMissions}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
} 