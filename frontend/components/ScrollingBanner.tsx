export default function ScrollingBanner() {
  return (
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
} 