import { NextResponse } from 'next/server';
import { privy } from '../../../utils/privy-client';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { userId } = body;

    if (!userId) {
      return NextResponse.json(
        { error: 'User ID is required' },
        { status: 400 }
      );
    }

    // Reset user XP to 0
    await privy.setCustomMetadata(userId, {
      xp: 0,
    });

    return NextResponse.json({
      success: true,
      userId,
      newXp: 0,
      message: 'XP reset successfully'
    });
    
  } catch (error: unknown) {
    console.error('Reset XP error:', error);
    
    let errorMessage = 'Failed to reset XP';
    if (error && typeof error === 'object' && 'message' in error) {
      errorMessage = (error as Error).message;
    }
    
    return NextResponse.json(
      { error: errorMessage },
      { status: 500 }
    );
  }
} 