"use client"

import React, { useState, useEffect } from 'react';
import { usePrivy } from '@privy-io/react-auth';
import { MissionType } from '../../types/mission';
import Navbar from '../../components/Navbar';
import MissionList from '../../components/MissionList';
import MissionDetail from '../../components/MissionDetail';
import ScrollingBanner from '../../components/ScrollingBanner';

// Define the Privy User type with customData
interface PrivyUser {
  id: string;
  customMetadata?: {
    xp?: number;
  };
}

export default function MainPage() {
  const { user } = usePrivy();
  console.log(user);
  const privyUser = user as PrivyUser;
  const [selectedMission, setSelectedMission] = useState<MissionType | null>(null);
  const [missions, setMissions] = useState<MissionType[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const handleResetXP = async () => {
    if (!privyUser?.id) return;
    
    try {
      const response = await fetch('/api/reset-xp', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ userId: privyUser.id }),
      });

      if (!response.ok) {
        throw new Error('Failed to reset XP');
      }

      // Force a page refresh to update the XP display
      window.location.reload();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to reset XP');
    }
  };

  useEffect(() => {
    const fetchMissions = async () => {
      try {
        const response = await fetch('https://cors-anywhere.herokuapp.com/http://89.117.55.209:3001/api/quests/?skip=0&limit=100'); //'http://localhost:8000/api/quests/?skip=0&limit=100'); //'https://89.117.55.209:3443/api/quests/?skip=0&limit=100');
        if (!response.ok) {
          throw new Error('Failed to fetch missions');
        }
        const data = await response.json();
        setMissions(data.quests);
        setIsLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
        setIsLoading(false);
      }
    };

    fetchMissions();
  }, []);

  const handleMissionClick = (mission: MissionType) => {
    setSelectedMission(mission);
  };

  const handleBack = () => {
    setSelectedMission(null);
  };

  return (
    <div 
      className="absolute top-0 left-0 w-full z-0 from-black to-pink-900 bg-gradient-to-r" 
    >
      <div className='w-full h-full bg-black/65 flex flex-col justify-between min-h-screen'>
        <div className='grow flex flex-col gap-4 px-4'>
          <Navbar theme="dark" />
          
          {privyUser && (
            <div className="text-white bg-white/10 p-4 rounded-lg mb-4">
              <p>XP: {privyUser.customMetadata?.xp || 0}</p>
              <button
                onClick={handleResetXP}
                className="mt-2 bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-md transition-colors"
              >
                Reset XP
              </button>
            </div>
          )}

          {isLoading ? (
            <div className="text-white text-center py-8">Loading missions...</div>
          ) : error ? (
            <div className="text-red-500 text-center py-8">{error}</div>
          ) : selectedMission ? (
            <MissionDetail 
              mission={selectedMission}
              onBack={handleBack}
            />
          ) : (
            <MissionList 
              missions={missions}
              onMissionClick={handleMissionClick}
              onMissionsUpdate={setMissions}
            />
          )}
        </div>

        <ScrollingBanner />
      </div>
    </div>
  );
} 