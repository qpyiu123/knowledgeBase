import { Children, isValidElement, useRef, useState, type ReactNode } from 'react';
import ReactMarkdown from 'react-markdown';
import rehypeHighlight from 'rehype-highlight';
import remarkGfm from 'remark-gfm';

/** 把 React 子节点展开成纯文本（用于复制代码、生成标题 id）。 */
function nodeText(node: ReactNode): string {
  if (node == null || typeof node === 'boolean') return '';
  if (typeof node === 'string' || typeof node === 'number') return String(node);
  if (Array.isArray(node)) return node.map(nodeText).join('');
  if (isValidElement<{ children?: ReactNode }>(node)) return nodeText(node.props.children);
  return '';
}

export function slugify(text: string): string {
  return (
    text
      .toLowerCase()
      .replace(/`/g, '')
      .replace(/[^\w\u4e00-\u9fa5]+/g, '-')
      .replace(/^-+|-+$/g, '')
      .slice(0, 60) || 'sec'
  );
}

function CodeBlock({ lang, text, children }: { lang: string; text: string; children: ReactNode }) {
  const [done, setDone] = useState(false);
  const timer = useRef<number | undefined>(undefined);

  function copy() {
    navigator.clipboard
      .writeText(text)
      .then(() => {
        setDone(true);
        window.clearTimeout(timer.current);
        timer.current = window.setTimeout(() => setDone(false), 1400);
      })
      .catch(() => setDone(false));
  }

  return (
    <div className="code-wrap">
      <div className="code-head">
        <b>{lang || '代码'}</b>
        <button className="copy-btn" type="button" onClick={copy}>
          {done ? '已复制' : '复制'}
        </button>
      </div>
      <pre>{children}</pre>
    </div>
  );
}

export default function Md({ text }: { text: string }) {
  return (
    <div className="md">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[[rehypeHighlight, { detect: true, ignoreMissing: true }]]}
        components={{
          h1: ({ children }) => <h1 id={slugify(nodeText(children))}>{children}</h1>,
          h2: ({ children }) => <h2 id={slugify(nodeText(children))}>{children}</h2>,
          h3: ({ children }) => <h3 id={slugify(nodeText(children))}>{children}</h3>,
          h4: ({ children }) => <h4 id={slugify(nodeText(children))}>{children}</h4>,
          a: ({ href, children }) => (
            <a href={href} target="_blank" rel="noopener noreferrer">
              {children}
            </a>
          ),
          pre: ({ children }) => {
            const first = Children.toArray(children)[0];
            const className =
              isValidElement<{ className?: string }>(first) && first.props.className
                ? first.props.className
                : '';
            const lang = /language-([\w+-]+)/.exec(className)?.[1] ?? '';
            return (
              <CodeBlock lang={lang} text={nodeText(first)}>
                {children}
              </CodeBlock>
            );
          },
        }}
      >
        {text}
      </ReactMarkdown>
    </div>
  );
}
