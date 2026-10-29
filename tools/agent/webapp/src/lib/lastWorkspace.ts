export type StoredWorkspace = { id: string; title: string };

/** 默认工作区记忆键；旧版本用的是 ctf-kb-current-workspace。 */
export const LAST_WORKSPACE_KEY = 'last_workspace_id';
export const LEGACY_WORKSPACE_KEY = 'ctf-kb-current-workspace';

function parse(raw: string | null): StoredWorkspace | null {
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw) as StoredWorkspace;
    if (parsed && typeof parsed.id === 'string' && parsed.id) {
      return { id: parsed.id, title: String(parsed.title || parsed.id) };
    }
  } catch {
    // 损坏的本地记录直接忽略。
  }
  return null;
}

/** 读取默认工作区；新键不存在时回退旧键，便于升级后继续沿用。 */
export function loadLastWorkspace(): StoredWorkspace {
  try {
    return (
      parse(localStorage.getItem(LAST_WORKSPACE_KEY)) ||
      parse(localStorage.getItem(LEGACY_WORKSPACE_KEY)) || { id: '', title: '' }
    );
  } catch {
    return { id: '', title: '' };
  }
}

export function saveLastWorkspace(ws: StoredWorkspace): void {
  try {
    if (!ws.id) {
      clearLastWorkspace();
      return;
    }
    localStorage.setItem(LAST_WORKSPACE_KEY, JSON.stringify(ws));
    localStorage.removeItem(LEGACY_WORKSPACE_KEY);
  } catch {
    // localStorage 不可用时只保留内存状态。
  }
}

export function clearLastWorkspace(): void {
  try {
    localStorage.removeItem(LAST_WORKSPACE_KEY);
    localStorage.removeItem(LEGACY_WORKSPACE_KEY);
  } catch {
    // 忽略不可用的 localStorage。
  }
}
