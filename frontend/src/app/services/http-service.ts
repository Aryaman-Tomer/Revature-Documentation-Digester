import { Service } from '@angular/core';

export interface Source {
  filename: string;
  page: string;
  chunk_index: string;
  content: string;
}

export interface RagResponse {
  response: string;
  sources: Source[];
}

// ponytail: hardcoded backend URL, move to environment config when deploying
const BASE = 'http://localhost:8000/documents';

async function send<T>(path: string, init: RequestInit): Promise<T> {
  const res = await fetch(BASE + path, { method: 'POST', ...init });
  if (!res.ok) {
    const detail = (await res.json().catch(() => null))?.detail;
    throw new Error(typeof detail === 'string' ? detail : `Request failed (${res.status})`);
  }
  return res.json();
}

@Service()
export class HttpService {
  /** Resolves once the backend has embedded the document. */
  upload(file: File): Promise<unknown> {
    const body = new FormData();
    body.append('file', file);
    return send('/upload', { body });
  }

  ask(prompt: string): Promise<RagResponse> {
    return send('/ask', {
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt }),
    });
  }
}
