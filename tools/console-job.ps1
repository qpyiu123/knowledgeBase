# Windows 会在控制窗口关闭时释放 Job，结束其中的查询服务和子进程。
if (-not ('KbConsoleJob' -as [type])) {
    Add-Type -TypeDefinition @'
using System;
using System.ComponentModel;
using System.Diagnostics;
using System.Runtime.InteropServices;
using Microsoft.Win32.SafeHandles;

public sealed class KbConsoleJob : IDisposable {
    [StructLayout(LayoutKind.Sequential)]
    private struct BasicLimits {
        public long PerProcessUserTimeLimit, PerJobUserTimeLimit;
        public uint LimitFlags;
        public UIntPtr MinimumWorkingSetSize, MaximumWorkingSetSize;
        public uint ActiveProcessLimit;
        public UIntPtr Affinity;
        public uint PriorityClass, SchedulingClass;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct IoCounters {
        public ulong ReadOperations, WriteOperations, OtherOperations;
        public ulong ReadBytes, WriteBytes, OtherBytes;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct ExtendedLimits {
        public BasicLimits Basic;
        public IoCounters Io;
        public UIntPtr ProcessMemoryLimit, JobMemoryLimit, PeakProcessMemory, PeakJobMemory;
    }

    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern SafeFileHandle CreateJobObject(IntPtr attributes, string name);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool SetInformationJobObject(SafeFileHandle job, int infoClass,
        ref ExtendedLimits limits, uint size);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool AssignProcessToJobObject(SafeFileHandle job, IntPtr process);

    private readonly SafeFileHandle handle;

    public KbConsoleJob() {
        handle = CreateJobObject(IntPtr.Zero, null);
        if (handle.IsInvalid) throw new Win32Exception(Marshal.GetLastWin32Error());
        var limits = new ExtendedLimits();
        limits.Basic.LimitFlags = 0x2000; // JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        const int extendedLimitInformation = 9;
        if (!SetInformationJobObject(handle, extendedLimitInformation, ref limits,
                (uint)Marshal.SizeOf(typeof(ExtendedLimits)))) {
            var error = new Win32Exception(Marshal.GetLastWin32Error());
            handle.Dispose();
            throw error;
        }
    }

    public void Add(Process process) {
        if (!AssignProcessToJobObject(handle, process.Handle))
            throw new Win32Exception(Marshal.GetLastWin32Error());
    }

    public void Dispose() {
        handle.Dispose();
    }
}
'@
}

function Start-KbConsoleWeb {
    param([string]$Python, [string]$Script, [string]$Root, [string]$LogDir,
          [string]$GateName, [KbConsoleJob]$Job, [Threading.EventWaitHandle]$Gate)

    # 先把等待中的启动进程加入 Job，再让它启动 Python（含虚拟环境启动器）。
    $pythonArg = $Python.Replace("'", "''")
    $scriptArg = $Script.Replace("'", "''")
    $stdout = (Join-Path $LogDir 'web.log').Replace("'", "''")
    $stderr = (Join-Path $LogDir 'web.err.log').Replace("'", "''")
    $command = @"
`$ErrorActionPreference = 'Stop'
`$gate = [Threading.EventWaitHandle]::OpenExisting('$GateName')
try { if (-not `$gate.WaitOne(10000)) { exit 1 } } finally { `$gate.Dispose() }
`$child = Start-Process -FilePath '$pythonArg' -ArgumentList @('"$scriptArg"') ``
    -RedirectStandardOutput '$stdout' -RedirectStandardError '$stderr' -WindowStyle Hidden -PassThru
`$child.WaitForExit()
exit `$child.ExitCode
"@
    $encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($command))
    $worker = Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'
    $process = Start-Process -FilePath $worker `
        -ArgumentList @('-NoLogo', '-NoProfile', '-NonInteractive', '-EncodedCommand', $encoded) `
        -WorkingDirectory $Root -WindowStyle Hidden -PassThru
    try {
        $Job.Add($process)
        $null = $Gate.Set()
    } catch {
        Stop-Process -InputObject $process -ErrorAction SilentlyContinue
        throw
    }
    return $process
}
