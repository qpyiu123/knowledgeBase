import { Alert, Button, Group, NumberInput, Paper, Select, Stack, Switch, Text, TextInput, Title } from "@mantine/core";
import { useEffect, useState } from "react";
import { api, type Settings, type SettingValue } from "../api";

const names: Record<string, string> = {
  auto: "跟随系统", light: "浅色", dark: "深色", on_demand: "按需启动",
  manual: "仅手动启动", off: "关闭", cpu: "CPU", vulkan: "Vulkan",
  zh: "中文", en: "英语", "qwen35-9b": "Qwen3.5 9B", "qwen35-4b": "Qwen3.5 4B",
};

export default function SettingsPage({ onSaved }: { onSaved: (settings: Settings) => void }) {
  const [data, setData] = useState<Settings>();
  const [changes, setChanges] = useState<Record<string, SettingValue>>({});
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const [starting, setStarting] = useState(false);
  const [advanced, setAdvanced] = useState(false);

  useEffect(() => {
    let active = true;
    api.settings().then(value => { if (active) setData(value); })
      .catch(e => { if (active) setError(String(e.message || e)); });
    return () => { active = false; };
  }, []);
  useEffect(() => {
    if (!starting && data?.index_update?.state !== "running") return;
    const timer = window.setInterval(() => api.settings().then(setData).catch(() => {}), 800);
    return () => window.clearInterval(timer);
  }, [starting, data?.index_update?.state]);

  const update = (key: string, value: SettingValue) => setChanges(previous => ({ ...previous, [key]: value }));
  const save = async () => {
    setSaving(true); setError(""); setNotice("");
    try {
      const next = await api.saveSettings(changes);
      setData(next); setChanges({}); onSaved(next); setNotice("设置已保存");
    } catch (e) { setError((e as Error).message); }
    finally { setSaving(false); }
  };
  const control = async (action: "start" | "stop" | "restart") => {
    setError(""); setNotice("");
    if (action !== "stop") setStarting(true);
    try { setData(await api.model(action)); }
    catch (e) { setError((e as Error).message); }
    finally { if (action !== "stop") setStarting(false); }
  };

  const groups = [...new Set(data?.fields.map(field => field.group))];
  return <Stack gap="md" px="lg" py="md">
    <Title order={2}>设置</Title>
    {error && <Alert color="red">{error}</Alert>}
    {notice && <Text role="status">{notice}</Text>}
    {!data && !error && <Text>正在读取设置…</Text>}
    {data && groups.map(group => <Paper key={group} withBorder p="md">
      <Stack gap="sm">
        <Title order={3}>{group}</Title>
        {group === "模型" && <>
          <Text role="status">当前：{starting || data.model.state === "loading" ? "正在启动" :
            data.model.state === "ready" ? (names[data.model.model || ""] || data.model.model) : "未启动"}</Text>
          {data.forced_off && <Text>本次启动仅允许查询。要使用解释，请正常重新启动应用。</Text>}
          {data.model.error && <Text c="red">{data.model.error}</Text>}
          <Group>
            <Button size="xs" disabled={starting || data.forced_off || saving} onClick={() => void control("start")}>启动</Button>
            <Button size="xs" variant="default" onClick={() => void control("stop")}>停止</Button>
            <Button size="xs" variant="default" disabled={starting || data.forced_off || saving} onClick={() => void control("restart")}>重启模型</Button>
          </Group>
        </>}
        {group === "高级" && <Button variant="subtle" size="xs" onClick={() => setAdvanced(!advanced)}>{advanced ? "收起高级选项" : "展开高级选项"}</Button>}
        {(group !== "高级" || advanced) && data.fields.filter(field => field.group === group).map(field => {
          const value = changes[field.key] ?? field.value;
          const description = field.override ? `本次由 ${field.override} 指定：${field.effective}` :
            field.effective !== field.value ? `${field.apply}生效；当前：${field.effective}` : `${field.apply}生效`;
          if (field.options.length) return <Select key={field.key} label={field.label} description={description}
            data={field.options.map(option => ({ value: option, label: names[option] || option }))}
            allowDeselect={false} value={String(value)} onChange={next => { if (next !== null) update(field.key, next); }} />;
          if (field.kind === "bool") return <Switch key={field.key} label={field.label}
            checked={Boolean(value)} onChange={event => update(field.key, event.currentTarget.checked)} />;
          if (field.kind === "int" || field.kind === "float") return <NumberInput key={field.key} label={field.label}
            description={description} value={typeof value === "boolean" ? Number(value) : value} min={field.limits[0]} max={field.limits[1]}
            allowDecimal={field.kind === "float"} step={field.kind === "float" ? 0.1 : 1}
            onChange={next => update(field.key, next)} />;
          return <TextInput key={field.key} label={field.label} description={description}
            value={String(value)} onChange={event => update(field.key, event.currentTarget.value)} />;
        })}
        {group === "搜索与索引" && <Group>
          <Button variant="default" size="xs" loading={data.index_update?.state === "running"}
            onClick={() => { setError(""); api.reindex().then(setData).catch(e => setError(e.message)); }}>更新索引</Button>
          {data.index_update?.message && <Text size="sm" role="status">{data.index_update.message}</Text>}
        </Group>}
      </Stack>
    </Paper>)}
    {data && <Group><Button loading={saving} disabled={!Object.keys(changes).length} onClick={() => void save()}>保存设置</Button></Group>}
  </Stack>;
}
