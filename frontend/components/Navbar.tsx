import Link from 'next/link';
import { usePrivy } from '@privy-io/react-auth';

type NavbarProps = {
  theme?: 'light' | 'dark';
};

export default function Navbar({ theme = 'light' }: NavbarProps) {
  const { authenticated, login } = usePrivy();

  const textColor = theme === 'light' ? 'text-gray-900' : 'text-white';
  const hoverColor = theme === 'light' ? 'hover:text-gray-700' : 'hover:text-gray-300';
  const buttonBg = theme === 'light' ? 'bg-black text-white hover:bg-gray-800' : 'bg-white text-black hover:bg-gray-100';

  return (
    <nav className="relative z-10 px-6 py-6">
      <div className={"mx-auto flex justify-between items-center " + (theme === 'light' ? 'max-w-7xl' : '')}>
        <Link href="/" className={`text-xl font-medium ${textColor}`}>Chiliz Quest</Link>
        <div className="flex items-center gap-8">
          <Link 
            href="/leaderboard"
            className={`${textColor} ${hoverColor} transition-colors`}
          >
            Leaderboard
          </Link>
          {authenticated ? (
            <Link 
              href="/main"
              className={`px-4 py-2 rounded-lg ${buttonBg} transition-colors`}
            >
              Dashboard
            </Link>
          ) : (
            <button
              onClick={login}
              className={`px-4 py-2 rounded-lg ${buttonBg} transition-colors`}
            >
              Connect Wallet
            </button>
          )}
        </div>
      </div>
    </nav>
  );
} 