// components/audio-player.tsx
import { Card } from "@/components/ui/card"

interface AudioPlayerProps {
  audioUrl: string | null;
  isLoading: boolean;
}

export default function AudioPlayer({ audioUrl, isLoading }: AudioPlayerProps) {
  if (isLoading) {
    return (
      <Card className="w-full p-4 mb-4">
        <div className="animate-pulse h-12 bg-gray-200 rounded"></div>
      </Card>
    )
  }

  if (!audioUrl) return null;

  // The audioUrl should now be a full URL from the backend
  return (
    <Card className="w-full p-4 mb-4">
      <audio 
        controls 
        className="w-full" 
        src={audioUrl}  // Use the full URL directly
      >
        Your browser does not support the audio element.
      </audio>
    </Card>
  )
}