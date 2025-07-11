import { MissionType } from '../types/mission';

interface MissionDetailProps {
  mission: MissionType;
  onBack: () => void;
}

export default function MissionDetail({ mission, onBack }: MissionDetailProps) {
  return (
    <div className='flex flex-col gap-4 items-center justify-center h-full grow'>
      <div className='bg-white p-8 w-full max-w-2xl relative'>
        <div className='absolute top-0 left-0 w-1 h-1 bg-black'></div>
        <div className='absolute top-0 right-0 w-1 h-1 bg-black'></div>
        <div className='absolute bottom-0 left-0 w-1 h-1 bg-black'></div>
        <div className='absolute bottom-0 right-0 w-1 h-1 bg-black'></div>
        <div className='flex justify-between items-center mb-6'>
          <h2 className='text-2xl font-bold'>{mission.name}</h2>
          <button 
            onClick={onBack}
            className='px-4 py-2 bg-gray-200 rounded-md hover:bg-gray-300 transition-all'
          >
            Back to Missions
          </button>
        </div>
        <p className='text-lg'>{mission.description}</p>
        <button className='mt-6 w-full bg-black text-white py-3 rounded-md hover:bg-black/90 transition-all'>
          Complete Mission
        </button>
      </div>
    </div>
  );
} 