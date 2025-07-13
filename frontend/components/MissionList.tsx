import { useState } from 'react';
import type { MissionType } from '@/types/mission';

interface MissionListProps {
  missions: MissionType[];
  onMissionClick: (mission: MissionType) => void;
  onMissionsUpdate: (missions: MissionType[]) => void;
}

export default function MissionList({ missions, onMissionClick, onMissionsUpdate }: MissionListProps) {
  const [isLoading, setIsLoading] = useState(false);

  const handleGenerateMissions = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('http://cors-anywhere.herokuapp.com/http://89.117.55.209:3001/api/quests/generate/all'); //'http://localhost:8000/api/quests/generate/all');
      if (!response.ok) {
        throw new Error('Failed to generate missions');
      }
      const newMissions = await response.json();
      onMissionsUpdate(newMissions);
    } catch (error) {
      console.error('Error generating missions:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-4">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 p-4">
        <h2 className="col-span-full text-2xl font-bold text-white mb-4">Individual Missions</h2>
        {missions
          .filter(mission => mission.quest_type === 'individual')
          .map((mission) => (
          <div
            key={mission.id}
            className="backdrop-blur-sm bg-white/15 border border-white/20 shadow-lg p-6 rounded-lg cursor-pointer transition-all hover:bg-white/20"
            onClick={() => onMissionClick(mission)}
          >
            <h3 className="text-xl font-bold text-white mb-2">{mission.title}</h3>
            <p className="text-white/80 mb-4">{mission.description.slice(0, 100)}...</p>
            <div className="flex justify-between items-center text-sm">
              <span className="bg-white/20 backdrop-blur-sm text-white px-2 py-1 rounded-md">Difficulty: {mission.difficulty}</span>
              <div className="flex gap-4">
                <span className="text-white/80">XP: {mission.xp_reward}</span>
                <span className="text-white/80">Points: {mission.points_reward}</span>
              </div>
            </div>
          </div>
        ))}

        <h2 className="col-span-full text-2xl font-bold text-white mb-4 mt-8">Other Missions</h2>
        {missions
          .filter(mission => mission.quest_type !== 'individual')
          .map((mission) => (
          <div
            key={mission.id}
            className="backdrop-blur-sm bg-white/15 border border-white/20 shadow-lg p-6 rounded-lg cursor-pointer transition-all hover:bg-white/20"
            onClick={() => onMissionClick(mission)}
          >
            <h3 className="text-xl font-bold text-white mb-2">{mission.title}</h3>
            <p className="text-white/80 mb-4">{mission.description.slice(0, 100)}...</p>
            <div className="flex justify-between items-center text-sm">
              <span className="bg-white/20 backdrop-blur-sm text-white px-2 py-1 rounded-md">Difficulty: {mission.difficulty}</span>
              <div className="flex gap-4">
                <span className="text-white/80">XP: {mission.xp_reward}</span>
                <span className="text-white/80">Points: {mission.points_reward}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
      <div className="flex p-4 pb-8">
        <button 
          className={`bg-white text-black px-4 py-4 rounded-md hover:bg-gray-100 transition-colors ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
          onClick={handleGenerateMissions}
          disabled={isLoading}
        >
          {isLoading ? 'Generating...' : 'Generate New Missions'}
        </button>
      </div>
    </div>
  );
} 