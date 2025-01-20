```mermaid
journey
    title New Podcast Newsletter
    section Find new episodes      
      Find new episodes by cutoff: 2: Monitor
      Persist mp3s to transcribe: 2: Monitor
    section Transcribe
      Check if transcription exists: 2: Lookup S3
      Transcribe with Whisper: 15: Whisper
      Persist in S3: 3: S3 
    section Summarize
      Check if summary exists: 3: Lookup S3
      Summarize: 8: Ollama
      Persist in S3: 3: S3
    section EMail
      Send Email: 3: Mailjet
```