import { afterEach, describe, expect, it, vi } from 'vitest';
import { ask } from './api';
import { extractSSEEvents } from './lib/sse';

function streamFrom(chunks: Uint8Array[]): ReadableStream<Uint8Array> {
  return new ReadableStream<Uint8Array>({
    start(controller) {
      for (const c of chunks) controller.enqueue(c);
      controller.close();
    },
  });
}

/** 把字节流切碎，模拟网络分块（包括切在多字节 UTF-8 中间）。 */
function splitBytes(text: string, size = 3): Uint8Array[] {
  const bytes = new TextEncoder().encode(text);
  const out: Uint8Array[] = [];
  for (let i = 0; i < bytes.length; i += size) out.push(bytes.slice(i, i + size));
  return out;
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('extractSSEEvents', () => {
  it('keeps a partial event across chunks', () => {
    const first = extractSSEEvents('data: {"t":"tok","v":"你');
    expect(first.events).toHaveLength(0);
    expect(first.rest).toContain('你');

    const second = extractSSEEvents(first.rest + '"}\n\n');
    expect(second.events).toEqual([{ t: 'tok', v: '你' }]);
    expect(second.rest).toBe('');
  });

  it('accepts CRLF delimiters and multiple events', () => {
    const { events } = extractSSEEvents(
      'data: {"t":"tok","v":"a"}\r\n\r\ndata: {"t":"done","info":"ok"}\r\n\r\n',
    );
    expect(events).toEqual([
      { t: 'tok', v: 'a' },
      { t: 'done', info: 'ok' },
    ]);
  });
});

describe('ask SSE 契约', () => {
  it('handles chunked UTF-8, tok and done info', async () => {
    const body =
      'data: {"t":"tok","v":"你"}\n\n' +
      'data: {"t":"tok","v":"好"}\n\n' +
      'data: {"t":"done","info":"2 tok · 1.0 tok/s"}\n\n';
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => new Response(streamFrom(splitBytes(body)), { status: 200 })),
    );

    const tokens: string[] = [];
    const done: string[] = [];
    const errors: string[] = [];
    await ask('问题', ['crypto/a.md'], {
      onToken: (t) => tokens.push(t),
      onDone: (info) => done.push(info),
      onError: (m) => errors.push(m),
    });

    expect(tokens.join('')).toBe('你好');
    expect(done).toEqual(['2 tok · 1.0 tok/s']);
    expect(errors).toEqual([]);
  });

  it('surfaces t=err instead of silently swallowing it', async () => {
    const body = 'data: {"t":"err","v":"模型不可达"}\n\n';
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => new Response(streamFrom(splitBytes(body)), { status: 200 })),
    );

    const errors: string[] = [];
    const done: string[] = [];
    await ask('问题', ['crypto/a.md'], {
      onToken: () => {},
      onError: (m) => errors.push(m),
      onDone: (info) => done.push(info),
    });

    expect(errors).toEqual(['模型不可达']);
    expect(done).toEqual([]);
  });

  it('reports an empty response when the stream ends with nothing', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => new Response(streamFrom([]), { status: 200 })),
    );

    const errors: string[] = [];
    await ask('问题', ['crypto/a.md'], {
      onToken: () => {},
      onError: (m) => errors.push(m),
    });

    expect(errors).toHaveLength(1);
    expect(errors[0]).toContain('模型没有返回内容');
  });

  it('shows a busy 429 message from the JSON error body', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(
        async () =>
          new Response(JSON.stringify({ error: '模型正在处理上一条问题' }), {
            status: 429,
            headers: { 'Content-Type': 'application/json' },
          }),
      ),
    );

    await expect(
      ask('问题', ['crypto/a.md'], { onToken: () => {} }),
    ).rejects.toThrow(/模型正在处理上一条问题.*429/);
  });

  it('propagates cancellation as AbortError', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(
        (_url: string, init?: RequestInit) =>
          new Promise<Response>((_resolve, reject) => {
            init?.signal?.addEventListener('abort', () => {
              reject(new DOMException('Aborted', 'AbortError'));
            });
          }),
      ),
    );

    const ctrl = new AbortController();
    const p = ask(
      '问题',
      ['crypto/a.md'],
      { onToken: () => {} },
      ctrl.signal,
    );
    ctrl.abort();
    await expect(p).rejects.toMatchObject({ name: 'AbortError' });
  });
});
