import { beforeEach, describe, expect, it, vi } from 'vitest';
import {
  LAST_WORKSPACE_KEY,
  LEGACY_WORKSPACE_KEY,
  clearLastWorkspace,
  loadLastWorkspace,
  saveLastWorkspace,
} from './lastWorkspace';

beforeEach(() => {
  localStorage.clear();
  vi.restoreAllMocks();
});

describe('last workspace memory', () => {
  it('saves and loads the default workspace under last_workspace_id', () => {
    saveLastWorkspace({ id: 'ws1', title: '示例工作区' });

    expect(localStorage.getItem(LAST_WORKSPACE_KEY)).toContain('ws1');
    expect(loadLastWorkspace()).toEqual({ id: 'ws1', title: '示例工作区' });
  });

  it('falls back to the legacy key and clears both', () => {
    localStorage.setItem(
      LEGACY_WORKSPACE_KEY,
      JSON.stringify({ id: 'old', title: '旧工作区' }),
    );
    expect(loadLastWorkspace()).toEqual({ id: 'old', title: '旧工作区' });

    clearLastWorkspace();
    expect(localStorage.getItem(LAST_WORKSPACE_KEY)).toBeNull();
    expect(localStorage.getItem(LEGACY_WORKSPACE_KEY)).toBeNull();
    expect(loadLastWorkspace()).toEqual({ id: '', title: '' });
  });

  it('ignores corrupted stored values', () => {
    localStorage.setItem(LAST_WORKSPACE_KEY, '{not json');
    expect(loadLastWorkspace()).toEqual({ id: '', title: '' });
  });
});
