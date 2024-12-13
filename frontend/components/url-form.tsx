'use client'

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Form } from "@/components/ui/form"
import { useState } from "react"

export function UrlForm() {
  const [url, setUrl] = useState("")
  
  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    // TODO: Implement submission
  }

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <Input 
        type="url" 
        placeholder="Enter article URL..." 
        value={url}
        onChange={(e) => setUrl(e.target.value)}
      />
      <Button type="submit">Convert to Audio</Button>
    </form>
  )
}
