"use client"

import React, { useState, useEffect } from 'react';
import { MissionType } from '../../types/mission';
import Navbar from '../../components/Navbar';
import MissionList from '../../components/MissionList';
import MissionDetail from '../../components/MissionDetail';
import ScrollingBanner from '../../components/ScrollingBanner';

export default function MainPage() {
  const [selectedMission, setSelectedMission] = useState<MissionType | null>(null);
  const [missions, setMissions] = useState<MissionType[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMissions = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/quests/?skip=0&limit=100');
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