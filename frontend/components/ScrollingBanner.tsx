"use client"

import React from 'react';

const ScrollingBanner: React.FC = () => {
  return (
    <div className="flex flex-col bg-black justify-between min-h-screen absolute top-0 left-0 w-full z-0">
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

      <div className='grow flex flex-col gap-2 px-4'>
      <p className='text-white text-2xl font-bold'>Missions</p>
        <div className='flex flex-row gap-2'>
        {Array.from({ length: 10 }).map((_, index) => (
        <div className='bg-white w-fit px-4 py-2 h-fit flex items-center justify-center relative hover:bg-white/90'>
          <div className='absolute top-0 left-0 w-1 h-1 bg-black'></div>
          <div className='absolute top-0 right-0 w-1 h-1 bg-black'></div>
          <div className='absolute bottom-0 left-0 w-1 h-1 bg-black'></div>
          <div className='absolute bottom-0 right-0 w-1 h-1 bg-black'></div>

          <p className='text-black font-bold'>Send a Tweet</p>
        </div>
        ))}
        </div>
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
  );
};

export default ScrollingBanner; 