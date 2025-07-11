"use client";

import { PrivyProvider } from '@privy-io/react-auth';
import { PropsWithChildren } from 'react';
import { mainnet } from 'wagmi/chains';

export default function Providers({ children }: PropsWithChildren) {
  return (
    <PrivyProvider
      appId={'cmcz6oibc01epjv0m65jxiobj'}
      config={{
        loginMethods: ['wallet', 'email'],
        appearance: {
          theme: 'dark',
          accentColor: '#000000',
          showWalletLoginFirst: true,
        },
        defaultChain: mainnet,
        supportedChains: [mainnet],
      }}
    >
      {children}
    </PrivyProvider>
  );
} 