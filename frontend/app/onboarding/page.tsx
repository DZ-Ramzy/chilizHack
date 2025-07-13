"use client"

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface Team {
  id: number;
  name: string;
  display_name: string;
  sport: string;
  league: string;
  logo_url: string | null;
  is_active: boolean;
}

export default function OnboardingPage() {
  const [teams, setTeams] = useState<Team[]>([]);
  const [selectedTeams, setSelectedTeams] = useState<number[]>([]);
  const router = useRouter();

  useEffect(() => {
    const fetchTeams = async () => {
      try {
        const response = await fetch('https://cors-anywhere.herokuapp.com/http://89.117.55.209:3001/api/teams/'); //'http://localhost:8001/api/teams');
        const data = await response.json();
        setTeams(data);
      } catch (error) {
        console.error('Error fetching teams:', error);
      }
    };

    fetchTeams();
  }, []);

  const toggleTeamSelection = (teamId: number) => {
    setSelectedTeams(prev => {
      if (prev.includes(teamId)) {
        return prev.filter(id => id !== teamId);
      } else {
        return [...prev, teamId];
      }
    });
  };

  const handleContinue = () => {
    if (selectedTeams.length > 0) {
      router.push('/main');
    }
  };

  return (
    <div className="min-h-screen w-full relative overflow-hidden"
      style={{
        backgroundImage: 'url(/bg.jpg)',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
      }}
    >
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" />
      
      <div className="relative z-10 min-h-screen flex items-center justify-center px-4 py-12">
        <div className="max-w-5xl w-full">
          <div className="bg-black/40 backdrop-blur-md rounded-3xl p-8 md:p-12 border border-white/10">
            <div className="text-center mb-12">
              <h1 className="text-4xl md:text-5xl font-bold text-white mb-6">
                Choose Your Favorite Teams
              </h1>
              <p className="text-xl text-white/90">
                Select the teams you want to follow and support
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 mb-8">
              {teams.map((team) => (
                <button
                  key={team.id}
                  onClick={() => toggleTeamSelection(team.id)}
                  className={`p-6 rounded-xl border transition-all duration-300 text-left ${
                    selectedTeams.includes(team.id)
                      ? 'bg-gradient-to-r from-red-500/20 to-orange-500/20 border-orange-500'
                      : 'bg-black/30 border-white/10 hover:bg-black/40'
                  }`}
                >
                  <div className="flex items-center gap-4">
                    {team.logo_url ? (
                      <img
                        src={team.logo_url}
                        alt={team.name}
                        className="w-12 h-12 object-contain"
                      />
                    ) : (
                      <div className="w-12 h-12 bg-white/10 rounded-full flex items-center justify-center">
                        <span className="text-2xl text-white/70">
                          {team.name.charAt(0)}
                        </span>
                      </div>
                    )}
                    <div>
                      <h3 className="text-xl font-semibold text-white">
                        {team.display_name}
                      </h3>
                      <p className="text-white/70">
                        {team.league}
                      </p>
                    </div>
                  </div>
                </button>
              ))}
            </div>

            <div className="flex justify-center">
              <button
                onClick={handleContinue}
                disabled={selectedTeams.length === 0}
                className={`px-8 py-4 rounded-full font-bold text-lg transition-all duration-300 ${
                  selectedTeams.length > 0
                    ? 'bg-gradient-to-r from-red-500 to-orange-500 text-white hover:scale-105'
                    : 'bg-gray-500/50 text-white/50 cursor-not-allowed'
                }`}
              >
                Continue
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 