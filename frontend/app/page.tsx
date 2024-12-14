'use client'

import { useState, FormEvent, useEffect, useRef } from 'react'
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import AudioPlayer from '@/components/audio-player'
import { API_URL } from "@/lib/config"

import CopyFeedButton from '@/components/copy-feed-button'

import { FaLink, FaFileAlt, FaHeadphones, FaPodcast } from 'react-icons/fa'

// Add delay utility at the top of the file
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

interface Word {
  content: string;
  lineBreak: boolean;
  isParagraphBreak?: boolean;
  headerLevel?: number;  // New: tracks header level (1-6)
}

export default function Home() {
  const [url, setUrl] = useState('')
  const [words, setWords] = useState<Word[]>([])
  const [audioUrl, setAudioUrl] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isGeneratingAudio, setIsGeneratingAudio] = useState(false)
  const eventSourceRef = useRef<EventSource | null>(null)

  // Add state for tracking stages
  const [stages, setStages] = useState({
    url: false,
    content: false,
    audio: false,
    podcast: false
  });
  const [loadingStage, setLoadingStage] = useState<keyof typeof stages | null>(null);

  // Helper function to get header styles based on level
  const getHeaderStyles = (level?: number) => {
    if (!level) return ''
    const sizes = {
      1: 'text-2xl font-bold leading-tight',
      2: 'text-xl font-bold leading-tight',
      3: 'text-lg font-bold leading-tight',
      4: 'text-base font-bold leading-tight',
      5: 'text-base font-semibold leading-tight',
      6: 'text-base font-medium leading-tight'
    }
    return sizes[level as keyof typeof sizes] || ''
  }

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

    // Reset all stages at start
    setStages({
      url: false,
      content: false,
      audio: false,
      podcast: false
    });
    
    setLoadingStage('url');
    await delay(1000); // Minimum 1s for URL stage
    setStages(prev => ({ ...prev, url: true }));

    setLoadingStage('content');
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
              isParagraphBreak: data.isParagraphBreak,
              headerLevel: data.headerLevel
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
                isParagraphBreak: data.isParagraphBreak,
                headerLevel: data.headerLevel
              }
            }
            return newWords
          })
          break
          
        case 'complete':
          setIsLoading(false)
          eventSourceRef.current?.close()
          setStages(prev => ({ ...prev, content: true }));
          setLoadingStage('audio');
          break
          
        case 'error':
          console.error(data.message)
          setIsLoading(false)
          eventSourceRef.current?.close()
          setLoadingStage(null);
          break
      }
    }

    try {
      // After content streaming completes
      await delay(1000); // Minimum 1s for content stage
      setStages(prev => ({ ...prev, content: true }));
      
      setLoadingStage('audio');
      await delay(1000); // Minimum 1s for audio stage
      const audioResponse = await fetch(`${API_URL}/api/generate-audio`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
      })
      const audioData = await audioResponse.json()
      setAudioUrl(`${API_URL}${audioData.audio_url}`)
      setStages(prev => ({ ...prev, audio: true }));
      
      setLoadingStage('podcast');
      await delay(1000); // Minimum 1s for podcast stage
      setStages(prev => ({ ...prev, podcast: true }));
      setLoadingStage(null);
    } catch (error) {
      console.error(error)
      setLoadingStage(null);
    } finally {
      setIsGeneratingAudio(false)
    }
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-6 bg-gray-50">

      <div className="flex items-center justify-center mb-8">
        <FaLink className={`w-6 h-6 transition-all duration-300 
          ${stages.url ? 'text-black' : 'text-gray-400'}
          ${loadingStage === 'url' ? 'animate-slow-pulse' : ''}`} 
        />
        <span className={`mx-2 transition-colors duration-300
          ${stages.url ? 'text-black' : 'text-gray-400'}`}>•</span>
        
        <FaFileAlt className={`w-6 h-6 transition-all duration-300
          ${stages.content ? 'text-black' : 'text-gray-400'}
          ${loadingStage === 'content' ? 'animate-slow-pulse' : ''}`}
        />
        <span className={`mx-2 transition-colors duration-300
          ${stages.content ? 'text-black' : 'text-gray-400'}`}>•</span>
        
        <FaHeadphones className={`w-6 h-6 transition-all duration-300
          ${stages.audio ? 'text-black' : 'text-gray-400'}
          ${loadingStage === 'audio' ? 'animate-slow-pulse' : ''}`}
        />
        <span className={`mx-2 transition-colors duration-300
          ${stages.audio ? 'text-black' : 'text-gray-400'}`}>•</span>
        
        <FaPodcast className={`w-6 h-6 transition-all duration-300
          ${stages.podcast ? 'text-black' : 'text-gray-400'}
          ${loadingStage === 'podcast' ? 'animate-slow-pulse' : ''}`}
        />
      </div>

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

      <div className="mt-6 w-full max-w-md">
        <AudioPlayer 
          audioUrl={audioUrl} 
          isLoading={isGeneratingAudio} 
        />
        {stages.podcast && <CopyFeedButton />}
      </div>

      {words.length > 0 && (
        <div className="mt-6 w-full max-w-md p-4 text-sm leading-relaxed rounded-md bg-white shadow-sm max-h-[60vh] overflow-y-auto">
          <div className="prose ">
            {words.map((word, index) => (
              <span key={index}>
                <span
                  className={`inline-block transition-opacity duration-100 ${
                    word.content ? 'opacity-100' : 'opacity-0'
                  } ${getHeaderStyles(word.headerLevel)}`}
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

    </main>
  )
}