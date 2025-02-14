
```mermaid
sequenceDiagram
    participant feeds as Feed Stores
    participant m as Monitor
    participant t as Transcription
    participant w as Whisper
    participant s3 
    participant summ as Summarizer
    participant o as Ollama

    participant mail as Mailjet <br/>Engine
    
    Note over m, feeds: Check for new feeds
    m -> m: If new Feed found <br/> create local file
    
    
    m ->>t: Start Transcription
    t->t: check if feeds <br/>to be transcribed
    t->s3: check if transcription already done
    Note over t, w: Transcribe new audio files

    t->>s3: store transcribed files as json.dump <br/>preserving episode metadata
    t->>m: transcription complete

      
    m->>summ: Summarize
    summ ->> s3: compare transcription and <br/>summary file names <br/>to decide what <br/> needs to be summarized
    Note over summ, o: Use local Ollama <br/> with LLama 3.2 to summarize
    summ ->> m: Summarization Complete
    m->>mail: Send Email

```