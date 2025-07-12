"use client"

import React, { useState } from 'react';
import { usePrivy } from '@privy-io/react-auth';
import { MissionType } from '../../types/mission';
import Header from '../../components/Header';
import MissionList from '../../components/MissionList';
import MissionDetail from '../../components/MissionDetail';
import ScrollingBanner from '../../components/ScrollingBanner';

export default function MainPage() {
  const { authenticated, user } = usePrivy();
  const [selectedMission, setSelectedMission] = useState<MissionType | null>(null);

  const missions = [
    {
      id: 1,
      name: 'Send a Tweet',
      description: 'Send a tweet to the Chiliz Quest Twitter account',
    },
    {
      id: 2,
      name: 'Follow Chiliz Quest on X',
      description: 'Follow Chiliz Quest on X',
    },
    {
      id: 3,
      name: 'Follow Chiliz Quest on Instagram',
      description: 'Follow Chiliz Quest on Instagram',
    },
    {
      id: 4,
      name: 'Follow Chiliz Quest on TikTok',
      description: 'Follow Chiliz Quest on TikTok',
    }
  ];

  const handleMissionClick = (mission: MissionType) => {
    setSelectedMission(mission);
  };

  const handleBack = () => {
    setSelectedMission(null);
  };

  return (
    <div 
      className="absolute top-0 left-0 w-full z-0" 
      style={{
        backgroundImage: 'url(/bg.jpg)',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
      }}
    >
      <div className='w-full h-full bg-black/65 flex flex-col justify-between min-h-screen pt-4'>
        <div className='grow flex flex-col gap-4 px-4'>
          <Header 
            authenticated={authenticated} 
            userAddress={user?.wallet?.address}
          />

          {selectedMission ? (
            <MissionDetail 
              mission={selectedMission}
              onBack={handleBack}
            />
          ) : (
            <MissionList 
              missions={missions}
              onMissionClick={handleMissionClick}
            />
          )}
        </div>

        <ScrollingBanner />
      </div>
    </div>
  );
} 