export type MissionType = {
  id: number;
  title: string;
  description: string;
  quest_type: string;
  status: string;
  team_name: string;
  team_id: number;
  user_id: number | null;
  target_metric: string;
  target_value: number;
  current_progress: number;
  xp_reward: number;
  points_reward: number;
  badges: string[];
  difficulty: string;
  created_at: string;
  metadata: Record<string, any>;
}; 