# URL to Podcast Converter - Frontend Documentation

## Overview
A Next.js 14 application that converts web articles into audio podcasts. The frontend provides a user-friendly interface for URL submission, content preview, and audio playback, while integrating with a FastAPI backend for content processing and audio generation.

## Project Structure

```
frontend/
├── app/                      # Next.js app directory
│   ├── layout.tsx           # Root layout with fonts and providers
│   └── page.tsx             # Main application page
├── components/              # React components
│   ├── ui/                 # shadcn components
│   ├── audio-player.tsx    # Audio playback interface
│   ├── copy-feed-button.tsx# RSS feed copy functionality
│   └── url-form.tsx        # URL submission form
├── hooks/                   # Custom React hooks
│   └── use-toast.ts        # Toast notification hook
└── lib/                     # Utility functions and configs
    ├── config.ts           # Environment configuration
    └── utils.ts            # Helper functions
```

## Key Components

### Page Component (`app/page.tsx`)
The main application page implements a multi-stage conversion process:

1. **Stage Management**
```typescript
const [stages, setStages] = useState({
  url: false,
  content: false,
  audio: false,
  podcast: false
});
```

2. **State Handling**
```typescript
interface Word {
  content: string;
  lineBreak: boolean;
  isParagraphBreak?: boolean;
  headerLevel?: number;
}

const [words, setWords] = useState<Word[]>([]);
const [audioUrl, setAudioUrl] = useState('');
const [isLoading, setIsLoading] = useState(false);
```

3. **Server-Sent Events**
- Uses EventSource for real-time content streaming
- Handles different event types: init, word, lineBreak, complete, error
- Maintains word array state for content preview

### Layout Component (`app/layout.tsx`)
- Implements Geist font family using next/font
- Provides toast notifications context
- Sets up metadata and HTML structure

## Component Architecture

### AudioPlayer Component
Properties:
```typescript
interface AudioPlayerProps {
  audioUrl: string;
  isLoading: boolean;
}
```
Features:
- HTML5 audio playback
- Loading state handling
- Error management

### UI Components (shadcn)
Core components used:
- Button: Form submissions and actions
- Input: URL entry field
- Toast: User notifications
- Card: Content containers

## State Management

The application uses React's useState for managing:
1. Form state (URL input)
2. Content preview state (words array)
3. Audio playback state
4. Loading states
5. Stage progression

## API Integration

### Endpoints
1. Content Extraction:
```typescript
const eventSource = new EventSource(
  `${API_URL}/api/extract/stream?url=${encodeURIComponent(url)}`
);
```

2. Audio Generation:
```typescript
const audioResponse = await fetch(`${API_URL}/api/generate-audio`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ url }),
});
```

## Feature Implementation

### Content Streaming
The application implements real-time content streaming:
1. Establishes SSE connection
2. Updates word array progressively
3. Handles formatting (paragraphs, headers)
4. Manages connection cleanup

### Progress Visualization
Visual feedback through four stages:
1. URL Processing (FaLink)
2. Content Extraction (FaFileAlt)
3. Audio Generation (FaHeadphones)
4. Podcast Feed Update (FaPodcast)

### Error Handling
1. Network errors
2. Invalid URLs
3. Content extraction failures
4. Audio generation failures

## Environment Configuration

Required environment variables:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000  # Backend API URL
```

## Development Setup

1. Installation:
```bash
npm install
```

2. Development Server:
```bash
npm run dev
```

3. Production Build:
```bash
npm run build
npm start
```

## Best Practices

1. **Component Organization**
   - Separate UI components from business logic
   - Use shadcn components for consistency
   - Implement proper TypeScript types

2. **State Management**
   - Use appropriate state scope
   - Implement proper cleanup in useEffect
   - Handle loading states comprehensively

3. **Error Handling**
   - Provide user feedback via toasts
   - Implement proper error boundaries
   - Handle network failures gracefully

4. **Performance**
   - Implement proper cleanup for EventSource
   - Use proper Next.js image optimization
   - Implement proper loading states

## Type Definitions

Key interfaces and types:
```typescript
interface Word {
  content: string;
  lineBreak: boolean;
  isParagraphBreak?: boolean;
  headerLevel?: number;
}

interface Stages {
  url: boolean;
  content: boolean;
  audio: boolean;
  podcast: boolean;
}
```

## Dependencies

Core dependencies:
- next: 15.1.0
- react: 19.0.0
- shadcn: UI component library
- react-icons: Icon components
- tailwindcss: Styling
- typescript: Type safety

