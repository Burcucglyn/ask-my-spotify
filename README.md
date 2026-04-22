# ask-my-spotify

A project to ask dummy questions about what I listen to on Spotify, and see my own built-in wrapped before the end of the year. :) 

**How did I end up with this idea?**

I want to spot patterns in when and where I listen to things over and over again: what my daily listening habits look like, which tracks give me better hype for the gym, how often I circle back to the same songs, and how long between those loops. Basically, instead of waiting for Spotify Wrapped once a year, build something I can interrogate whenever I feel like it. And learn it along the way... (RAG)


## How it works (RAG):

Quick idea:
- the LLM doesn't know my listening history, so I can't just ask it.
- RAG = turn my data into small text chunks, embed them, store them in a vector db.
- When I ask a question, pull the most relevant chunks and pass them to the MCP connection... I know you're bored now and stopped reading it, didn't you? 

**Stuff I still need to figure out:**
- Chunking strategy: per day? month? per artist? mix of all? need to test.
- Embedding model: Voyage vs something else, which one for this type of data?
- Vector DB: Chroma vs something simpler, what's easiest to start with?
- How many chunks to retrieve per question: 5? 10?
- Do I need metadata filtering (e.g. filter date range before semantic search) or is pure similarity enough?
- Eval: How do I even know if the answers are good? This is the biggest question... Although the answers will never be good enough...

** Will update this section as I figure things out ( if I don't forget of course) **

## Approach

I heard that Spotify API is well documented and gives good responses, soo time to test this hearing. Starting with the Spotify Web API to pull whatever I can get quickly. This keeps the scope small for v1 and lets me start building while the extended streaming history export is still on its way. Once the full export arrives, swap in the richer historical data without changing the rest of the pipeline.

## Scope for v1

- Recent listening history via the Spotify Web API.
- Audio features (tempo, energy, valence, etc.)
- A handful of question types: daily habits, gym tracks, repeat patterns.
- Local only, no deployment yet.


## Stack

Python, pandas, a database (vector store), FastAPI, Streamlit. Docker and Google Cloud Run possibly...

## Folder structure

```
ask-my-spotify/
├── src/          # ingest, chunk, embed, retrieve, generate
├── scripts/      # one-shot pipeline runners
├── notebooks/    # exploration
├── data/         # gitignored
└── README.md
```

## Status

Very early. Setting up the Spotify API connection first, extended export requested in parallel...

Let's start to create chaos!!

## Privacy

Code lives here, privacy first of course... As the famous philosopher Justin Bieber once said, " Is it too late now to say sorry? "
Data, and anything fetched from my listening history, stays local and gitignored. (might create synthetic data later so lazy people can play with it too as charity work)
