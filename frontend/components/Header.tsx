import { usePrivy } from '@privy-io/react-auth';
import Link from 'next/link';

interface HeaderProps {
  authenticated: boolean;
  userAddress?: string;
}

export default function Header({ authenticated, userAddress }: HeaderProps) {
  const { login } = usePrivy();

  return (
    <div className='flex flex-row justify-between items-center'>
      <Link href='/' className='text-white text-2xl font-bold'>Chiliz Quest</Link>
      {!authenticated ? (
        <button
          onClick={login}
          className='bg-white px-6 py-2 rounded-md font-bold hover:bg-white/90 transition-all'
        > 
          Connect Wallet
        </button>
      ) : (
        <p className='text-white'>Connected as {userAddress}</p>
      )}
    </div>
  );
} 