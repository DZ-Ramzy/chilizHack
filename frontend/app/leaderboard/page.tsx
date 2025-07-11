"use client"

import React from 'react';
import { usePrivy } from '@privy-io/react-auth';
import Header from '../../components/Header';
import ScrollingBanner from '../../components/ScrollingBanner';

type LeaderboardEntry = {
  rank: number;
  address: string;
  points: number;
  completedMissions: number;
};

// Exemple de données (à remplacer par des données réelles plus tard)
const leaderboardData: LeaderboardEntry[] = [
  { rank: 1, address: "0x1234...5678", points: 1500, completedMissions: 12 },
  { rank: 2, address: "0x8765...4321", points: 1200, completedMissions: 10 },
  { rank: 3, address: "0x9876...1234", points: 1000, completedMissions: 8 },
  { rank: 4, address: "0x4567...8901", points: 800, completedMissions: 7 },
  { rank: 5, address: "0x2345...6789", points: 600, completedMissions: 5 },
];

export default function LeaderboardPage() {
  const { authenticated, user } = usePrivy();

  return (
    <div 
      className="absolute top-0 left-0 w-full z-0" 
      style={{
        backgroundImage: 'url(/bg.jpg)',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
      }}
    >
      <div className='w-full h-full bg-black/70 flex flex-col justify-between min-h-screen pt-4'>
        <div className='grow flex flex-col gap-4 px-4'>
          <Header 
            authenticated={authenticated} 
            userAddress={user?.wallet?.address}
          />

          <div className="max-w-4xl mx-auto w-full">
            <div className="bg-black/40 backdrop-blur-md rounded-3xl p-8 border border-white/10">
              <h2 className="text-3xl font-bold text-white mb-8 text-center bg-gradient-to-r from-red-500 to-orange-500 bg-clip-text text-transparent">
                Leaderboard
              </h2>

              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="text-white/80 border-b border-white/10">
                      <th className="py-4 px-6 text-left">Rank</th>
                      <th className="py-4 px-6 text-left">Address</th>
                      <th className="py-4 px-6 text-right">Points</th>
                      <th className="py-4 px-6 text-right">Missions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {leaderboardData.map((entry) => (
                      <tr 
                        key={entry.address}
                        className="text-white/90 border-b border-white/5 hover:bg-white/5 transition-colors"
                      >
                        <td className="py-4 px-6">
                          <span className={`
                            inline-flex items-center justify-center w-8 h-8 rounded-full 
                            ${entry.rank === 1 ? 'bg-yellow-500' : 
                              entry.rank === 2 ? 'bg-gray-300' :
                              entry.rank === 3 ? 'bg-amber-700' : 'bg-white/10'}
                            font-bold
                          `}>
                            {entry.rank}
                          </span>
                        </td>
                        <td className="py-4 px-6 font-mono">{entry.address}</td>
                        <td className="py-4 px-6 text-right font-bold bg-gradient-to-r from-red-500 to-orange-500 bg-clip-text text-transparent">
                          {entry.points}
                        </td>
                        <td className="py-4 px-6 text-right">{entry.completedMissions}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        <ScrollingBanner />
      </div>
    </div>
  );
} 