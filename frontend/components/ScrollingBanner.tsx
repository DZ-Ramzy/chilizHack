"use client"

import React, { useState } from 'react';
import { usePrivy } from '@privy-io/react-auth';
import Mission from './Mission';

interface MissionType {
  id: number;
  name: string;
  description: string;
}

const ScrollingBanner: React.FC = () => {
  const { login, authenticated, user } = usePrivy();
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
  ]

  const handleMissionClick = (mission: MissionType) => {
    setSelectedMission(mission);
  };

  const handleBack = () => {
    setSelectedMission(null);
  };

  return (
    <div className="absolute top-0 left-0 w-full z-0" style={{
      backgroundImage: 'url(/bg.jpg)',
      backgroundSize: 'cover',
      backgroundPosition: 'center',
    }}>
      <div className='w-full h-full bg-black/70 flex flex-col justify-between min-h-screen pt-4'>
        <div className='grow flex flex-col gap-4 px-4'>
          <div className='flex flex-row justify-between items-center'>
            <p className='text-white text-2xl font-bold'>Chiliz Quest</p>
            {!authenticated ? (
              <button
                onClick={login}
                className='bg-white px-6 py-2 rounded-md font-bold hover:bg-white/90 transition-all'
              >
                Connect Wallet
              </button>
            ) : (
              <p className='text-white'>Connected as {user?.wallet?.address}</p>
            )}
          </div>

          {selectedMission ? (
            <div className='flex flex-col gap-4 items-center justify-center h-full grow'>
              <div className='bg-white p-8 w-full max-w-2xl relative'>
                <div className='absolute top-0 left-0 w-1 h-1 bg-black'></div>
                <div className='absolute top-0 right-0 w-1 h-1 bg-black'></div>
                <div className='absolute bottom-0 left-0 w-1 h-1 bg-black'></div>
                <div className='absolute bottom-0 right-0 w-1 h-1 bg-black'></div>
                <div className='flex justify-between items-center mb-6'>
                  <h2 className='text-2xl font-bold'>{selectedMission.name}</h2>
                  <button 
                    onClick={handleBack}
                    className='px-4 py-2 bg-gray-200 rounded-md hover:bg-gray-300 transition-all'
                  >
                    Back to Missions
                  </button>
                </div>
                <p className='text-lg'>{selectedMission.description}</p>
                <button className='mt-6 w-full bg-black text-white py-3 rounded-md hover:bg-black/90 transition-all'>
                  Complete Mission
                </button>
              </div>
            </div>
          ) : (
            <div className='flex flex-col gap-2 items-center justify-center h-full grow'>
              <div className='flex flex-col gap-4'>
                <p className='text-white text-2xl font-bold'>Your Missions</p>
                <p className='text-white'>Hey you have <span className='text-white font-bold'>10</span> missions to complete. Complete them to earn rewards.</p>
                <div className='flex flex-row gap-2 w-fit h-fit'>
                  {missions.map((mission) => (
                    <Mission 
                      key={mission.id} 
                      mission={mission} 
                      onClick={() => handleMissionClick(mission)}
                    />
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="bg-black/20 py-2 w-full overflow-hidden">
          <div
            style={{
              display: 'inline-block',
              whiteSpace: 'nowrap',
              animation: 'scrollLeft 60s linear infinite',
              paddingLeft: '0%',
            }}
          >
            <div className='flex flex-row gap-2'>
              {Array.from({ length: 50 }).map((_, index) => (
                <div key={index} className='flex flex-row gap-2 items-center'>
                  <p className='text-white text-xl font-semibold'>Chiliz Quest</p>
                  <div className='h-1 w-6 mx-4 bg-white'></div>
                </div>
              ))}
            </div>
          </div>
        </div>
        <style jsx>{`
          @keyframes scrollLeft {
            0% {
              transform: translateX(0);
            }
            100% {
              transform: translateX(-100%);
            }
          }
          @keyframes scrollRight {
            0% {
              transform: translateX(100%);
            }
            100% {
              transform: translateX(-200%);
            }
          }
        `}</style>
      </div>
    </div>
  );
};

export default ScrollingBanner; 