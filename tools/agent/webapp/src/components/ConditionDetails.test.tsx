import { MantineProvider } from '@mantine/core';
import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import ConditionDetails from './ConditionDetails';
import type { Applicability } from '../types';

const app: Applicability = {
  status: 'known', status_label: '已知',
  conditions: [{ id: 'same-n', label: '同一个 n', status: 'known', status_label: '已知',
    evidence: '查询证据：n1=15,n2=15', check: '比较 n' }],
  reading: [{ path: 'crypto/crt.md', title: 'CRT', present: true, missing: false }],
  guide: { id: 'common', title: 'RSA 共模：指数互素路径',
    source: { path: 'crypto/rsa.md', section: '二、原理', quote: 'gcd(e1,e2)=1' },
    next_check: '代回密文验证',
    contrasts: [{ path: 'crypto/broadcast.md', title: '对照广播', difference: '广播使用不同 n' }] },
};

describe('条件依据', () => {
  it('shows evidence, next checks and section navigation; reading stays separate', () => {
    const open = vi.fn();
    render(<MantineProvider><ConditionDetails app={app} onOpenDoc={open} /></MantineProvider>);
    fireEvent.click(screen.getByText('条件与下一步 · 已知'));
    expect(screen.getByText('查询证据：n1=15,n2=15')).toBeTruthy();
    expect(screen.getByText('下一步检查：代回密文验证')).toBeTruthy();
    fireEvent.click(screen.getByRole('button', { name: '查看依据：二、原理' }));
    expect(open).toHaveBeenLastCalledWith('crypto/rsa.md#二-原理', '二、原理');
    fireEvent.click(screen.getByRole('button', { name: '对照广播' }));
    expect(open).toHaveBeenLastCalledWith('crypto/broadcast.md', '对照广播');
    expect(screen.getByText('阅读依赖')).toBeTruthy();
    fireEvent.click(screen.getByRole('button', { name: 'CRT（本次已查到）' }));
    expect(open).toHaveBeenLastCalledWith('crypto/crt.md', 'CRT');
  });

  it('does not suggest executing a path whose conditions fail', () => {
    render(<MantineProvider><ConditionDetails app={{ ...app, status: 'unsatisfied', status_label: '不满足' }} onOpenDoc={() => {}} /></MantineProvider>);
    fireEvent.click(screen.getByText('条件与下一步 · 不满足'));
    expect(screen.queryByText(/代回密文验证/)).toBeNull();
    expect(screen.getByText('广播使用不同 n')).toBeTruthy();
  });

  it('hides no-rule boilerplate and shows missing reading without a broken button', () => {
    const { rerender } = render(<MantineProvider><ConditionDetails app={{ status: 'unknown', status_label: '未知', conditions: [] }} onOpenDoc={() => {}} /></MantineProvider>);
    expect(screen.queryByText(/条件与下一步/)).toBeNull();
    rerender(<MantineProvider><ConditionDetails app={{ status: 'unknown', status_label: '未知',
      reading: [{ path: null, title: '缺失资料', present: false, missing: true }] }} onOpenDoc={() => {}} /></MantineProvider>);
    fireEvent.click(screen.getByText('条件与下一步'));
    expect(screen.getByText('缺失资料（资料缺失）')).toBeTruthy();
    expect(screen.queryByRole('button')).toBeNull();
  });
});
