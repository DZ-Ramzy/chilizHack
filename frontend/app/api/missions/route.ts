import { NextResponse } from 'next/server';
import { privy } from '../../../utils/privy-client';

type PrivyMetadata = {
  [key: string]: string | number | boolean;
  xp: number;
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { userId, missionId, xpReward } = body;

    if (!userId || !missionId || !xpReward) {
      return NextResponse.json(
        { error: 'User ID, mission ID and XP reward are required' },
        { status: 400 }
      );
    }

    // Get current user data
    const user = await privy.getUser(userId);
    const currentXp = (user?.customMetadata as PrivyMetadata)?.xp || 0;
    
    // Update user XP
    const newXp = currentXp + xpReward;
    await privy.setCustomMetadata(userId, {
      xp: newXp,
    });

    // Update mission status in your database here if needed
    // TODO: Implement mission status update logic

    return NextResponse.json({
      success: true,
      userId,
      missionId,
      newXp,
      message: 'Mission completed successfully'
    });
    
  } catch (error: unknown) {
    console.error('Mission error:', error);
    
    let errorMessage = 'Failed to process mission';
    if (error && typeof error === 'object' && 'message' in error) {
      errorMessage = (error as Error).message;
    }
    
    return NextResponse.json(
      { error: errorMessage },
      { status: 500 }
    );
  }
} 