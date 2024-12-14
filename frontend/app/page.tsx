'use client'

import { useState, FormEvent } from 'react'
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import AudioPlayer from '@/components/audio-player'
import { API_URL } from "@/lib/config"

export default function Home() {
  const [url, setUrl] = useState('')
  const [content, setContent] = useState('')
  const [audioUrl, setAudioUrl] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      const response = await fetch(`${API_URL}/api/scrape`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
      })
      const data = await response.json()
      setContent(data.content)
      // Prefix the audio URL with the API base URL
      setAudioUrl(`${API_URL}${data.audio_url}`)
    } catch (error) {
      console.error(error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-6 bg-gray-50">
      <form onSubmit={handleSubmit} className="w-full max-w-md flex gap-2 mb-6">
        <Input
          type="url"
          value={url}
          onChange={e => setUrl(e.target.value)}
          placeholder="Enter URL"
          required
          className="flex-1"
        />
        <Button type="submit" disabled={isLoading}>
          {isLoading ? '...' : 'Go'}
        </Button>
      </form>

      <div className="mt-6 w-full max-w-md">
      <AudioPlayer audioUrl={audioUrl} isLoading={isLoading} />
      </div>

      {content && (
        <div className="mt-6 w-full max-w-md p-4 text-sm leading-relaxed rounded-md bg-white shadow-sm whitespace-pre-wrap">
          {content}
        </div>
      )}
    </main>
  )
}