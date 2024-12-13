import { Card } from "@/components/ui/card"

export default function AudioPlayer({ audioUrl, isLoading }) {
  if (isLoading) {
    return (
      <Card className="w-full p-4 mb-4">
        <div className="animate-pulse h-12 bg-gray-200 rounded"></div>
      </Card>
    )
  }

  if (!audioUrl) return null;

  return (
    <Card className="w-full p-4 mb-4">
      <audio 
        controls 
        className="w-full" 
        src={`http://localhost:8000${audioUrl}`}
      >
        Your browser does not support the audio element.
      </audio>
    </Card>
  )
}