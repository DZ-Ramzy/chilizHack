import { MissionType } from '../types/mission';
import Mission from './Mission';

interface MissionListProps {
  missions: MissionType[];
  onMissionClick: (mission: MissionType) => void;
}

export default function MissionList({ missions, onMissionClick }: MissionListProps) {
  return (
    <div className='flex flex-col gap-2 items-center justify-center h-full grow'>
      <div className='flex flex-col gap-4'>
        <p className='text-white text-2xl font-bold'>Your Missions</p>
        <p className='text-white'>
          Hey you have <span className='text-white font-bold'>10</span> missions to complete. Complete them to earn rewards.
        </p>
        <div className='flex flex-row gap-2 w-fit h-fit'>
          {missions.map((mission) => (
            <Mission 
              key={mission.id} 
              mission={mission} 
              onClick={() => onMissionClick(mission)}
            />
          ))}
        </div>
<<<<<<< HEAD
=======
        <button className='bg-white text-black px-4 py-2 rounded-lg'>Generate Missions</button>
>>>>>>> e97ca2b (feat: actual code)
      </div>
    </div>
  );
} 