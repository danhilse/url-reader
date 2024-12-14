'use client'

import { useState, FormEvent } from 'react'
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import AudioPlayer from '@/components/audio-player'
import { API_URL } from "@/lib/config"  // Add this import



export default function Home() {
  const [url, setUrl] = useState('')
  const [content, setContent] = useState('')
  const [audioUrl, setAudioUrl] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  console.log('Page rendered') // Add this to verify the page loads


  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      const response = await fetch(`${API_URL}/api/scrape`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      })
      
      const data = await response.json()
      setContent(data.content)
      setAudioUrl(data.audio_url)
    } catch (error) {
      console.error('Error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <main className="container mx-auto p-4 max-w-4xl">
      <h1 className="text-2xl font-bold mb-4">URL to Podcast Converter</h1>
      
      <form onSubmit={handleSubmit} className="mb-8">
        <div className="flex gap-2">
          <Input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Enter URL"
            required
            className="flex-1"
          />
          <Button type="submit" disabled={isLoading}>
            {isLoading ? 'Converting...' : 'Convert'}
          </Button>
        </div>
      </form>

      <AudioPlayer audioUrl={audioUrl} isLoading={isLoading} />
      
      {content && (
        <Card className="p-6 whitespace-pre-wrap">
          {content}
        </Card>
      )}
    </main>
  )
}