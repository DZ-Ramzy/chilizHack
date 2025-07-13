import { MissionType } from '../types/mission';
import { usePrivy } from '@privy-io/react-auth';
import { useState } from 'react';

interface MissionDetailProps {
  mission: MissionType;
  onBack: () => void;
}

export default function MissionDetail({ mission, onBack }: MissionDetailProps) {
  const { user } = usePrivy();
  const [isLoading, setIsLoading] = useState(false);

  const handleMissionAction = async () => {
    if (!user?.id) {
      alert('Please connect your wallet first');
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch('/api/missions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          userId: user.id,
          missionId: mission.id,
          action: mission.status === 'pending' ? 'start' : 'complete',
          xpReward: mission.xp_reward,
        }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || 'Failed to process mission action');
      }

      // You might want to refresh the mission data or update the UI here
      alert(data.message);
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to process mission action');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white/10 rounded-lg">
      <button 
        onClick={onBack}
        className="mb-6 text-white hover:text-gray-300 flex items-center gap-2"
      >
        <span>←</span> Back to Missions
      </button>
      
      <h2 className="text-2xl font-bold text-white mb-4">{mission.title}</h2>
      
      <div className="flex gap-4 mb-6">
        <span className="px-3 py-1 bg-yellow-400/20 text-yellow-400 rounded">
          {mission.difficulty}
        </span>
        <span className="px-3 py-1 bg-blue-400/20 text-blue-400 rounded">
          XP: {mission.xp_reward}
        </span>
        <span className="px-3 py-1 bg-green-400/20 text-green-400 rounded">
          Points: {mission.points_reward}
        </span>
      </div>

      <div className="text-gray-300 mb-6">
        {mission.description}
      </div>

      <div className="bg-white/5 p-4 rounded mb-6">
        <h3 className="text-white font-semibold mb-2">Progress</h3>
        <div className="flex items-center gap-4">
          <div className="flex-1 bg-gray-700 rounded-full h-2">
            <div 
              className="bg-blue-500 h-2 rounded-full" 
              style={{ width: `${(mission.current_progress / mission.target_value) * 100}%` }}
            />
          </div>
          <span className="text-white">
            {mission.current_progress} / {mission.target_value}
          </span>
        </div>
      </div>

      {mission.badges.length > 0 && (
        <div className="mb-6">
          <h3 className="text-white font-semibold mb-2">Badges to Earn</h3>
          <div className="flex gap-2">
            {mission.badges.map((badge, index) => (
              <span 
                key={index}
                className="px-3 py-1 bg-purple-400/20 text-purple-400 rounded"
              >
                {badge}
              </span>
            ))}
          </div>
        </div>
      )}

      <button 
        className="w-full bg-blue-500 text-white py-3 rounded hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        onClick={handleMissionAction}
        disabled={isLoading}
      >
        {isLoading ? 'Processing...' : mission.status === 'pending' ? 'Start Mission' : 'Complete Mission'}
      </button>
    </div>
  );
} 