import React from 'react';

interface AudioPlayerProps {
  audioUrl: string | null;
  isLoading: boolean;
}

const LoadingBars = () => {
  return (
    <div className="flex items-center justify-between w-full h-10 px-4 gap-0.5">
      {[...Array(24)].map((_, i) => (
        <div
          key={i}
          className="w-0.5 bg-primary/40 rounded-full animate-pulse"
          style={{
            height: `${Math.max(8, Math.min(24, (i % 3 + 1) * 8))}px`,
            animationDelay: `${i * 0.15}s`
          }}
        />
      ))}
    </div>
  );
};

export default function AudioPlayer({ audioUrl, isLoading }: AudioPlayerProps) {
  if (isLoading) {
    return (
      <div className="w-full mb-4 bg-muted/30 rounded-md">
        <LoadingBars />
      </div>
    );
  }

  if (!audioUrl) return null;

  return (
    <div className="w-full mb-4">
      <audio 
        controls 
        className="w-full" 
        src={audioUrl}
      >
        Your browser does not support the audio element.
      </audio>
    </div>
  );
}