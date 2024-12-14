'use client'

import { useState, FormEvent, useEffect, useRef } from 'react'
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import AudioPlayer from '@/components/audio-player'
import { API_URL } from "@/lib/config"

interface Word {
  content: string;
  lineBreak: boolean;
  isParagraphBreak?: boolean;  // New flag for paragraph breaks
}

export default function Home() {
  const [url, setUrl] = useState('')
  const [words, setWords] = useState<Word[]>([])
  const [audioUrl, setAudioUrl] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isGeneratingAudio, setIsGeneratingAudio] = useState(false)
  const eventSourceRef = useRef<EventSource | null>(null)

  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close()
      }
    }
  }, [])

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setIsLoading(true)
    setIsGeneratingAudio(true)
    setWords([])

    if (eventSourceRef.current) {
      eventSourceRef.current.close()
    }

    eventSourceRef.current = new EventSource(`${API_URL}/api/extract/stream?url=${encodeURIComponent(url)}`)
    
    eventSourceRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data)
      
      switch (data.type) {
        case 'init':
          setWords(new Array(data.total).fill({ content: '', lineBreak: false }))
          break
          
        case 'word':
          setWords(prev => {
            const newWords = [...prev]
            newWords[data.index] = { 
              content: data.content, 
              lineBreak: false,
              isParagraphBreak: data.isParagraphBreak 
            }
            return newWords
          })
          break
          
        case 'lineBreak':
          setWords(prev => {
            const newWords = [...prev]
            if (newWords[data.index]) {
              newWords[data.index] = { 
                ...newWords[data.index], 
                lineBreak: true,
                isParagraphBreak: data.isParagraphBreak 
              }
            }
            return newWords
          })
          break
          
        case 'complete':
          setIsLoading(false)
          eventSourceRef.current?.close()
          break
          
        case 'error':
          console.error(data.message)
          setIsLoading(false)
          eventSourceRef.current?.close()
          break
      }
    }

    try {
      const audioResponse = await fetch(`${API_URL}/api/generate-audio`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
      })
      const audioData = await audioResponse.json()
      setAudioUrl(`${API_URL}${audioData.audio_url}`)
    } catch (error) {
      console.error(error)
    } finally {
      setIsGeneratingAudio(false)
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
          disabled={isLoading}
        />
        <Button type="submit" disabled={isLoading}>
          Go
        </Button>
      </form>

      {words.length > 0 && (
        <div className="mt-6 w-full max-w-md p-4 text-sm leading-relaxed rounded-md bg-white shadow-sm">
          <div className="prose">
            {words.map((word, index) => (
              <span key={index}>
                <span
                  className={`inline-block transition-opacity duration-100 ${
                    word.content ? 'opacity-100' : 'opacity-0'
                  }`}
                >
                  {word.content || '•'}
                </span>
                {' '}
                {word.lineBreak && (
                  <>
                    <br />
                    {word.isParagraphBreak && <div className="h-4" />}
                  </>
                )}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="mt-6 w-full max-w-md">
        <AudioPlayer 
          audioUrl={audioUrl} 
          isLoading={isGeneratingAudio} 
        />
      </div>
    </main>
  )
}