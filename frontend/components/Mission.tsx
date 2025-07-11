import React from 'react';

interface MissionProps {
  mission: {
    id: number;
    name: string;
    description: string;
  };
  onClick: () => void;
}

const Mission: React.FC<MissionProps> = ({ mission, onClick }) => {
  return (
    <div 
      className='bg-white w-fit px-4 py-2 h-fit flex flex-col items-center justify-center relative hover:bg-white/90 cursor-pointer'
      onClick={onClick}
    >
      <div className='absolute top-0 left-0 w-1 h-1 bg-black'></div>
      <div className='absolute top-0 right-0 w-1 h-1 bg-black'></div>
      <div className='absolute bottom-0 left-0 w-1 h-1 bg-black'></div>
      <div className='absolute bottom-0 right-0 w-1 h-1 bg-black'></div>

      <p className='text-black font-bold'>{mission.name}</p>
    </div>
  );
};

export default Mission; 