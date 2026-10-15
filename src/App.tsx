import { useCallback, useEffect, useState } from 'react';
import { FileType2, LoaderCircle } from 'lucide-react';
import { AppFooter } from './components/AppFooter';
import { BrandHeader } from './components/BrandHeader';
import { ConversionSection } from './components/ConversionSection';
import { Intro } from './components/Intro';
import { MergeSection } from './components/MergeSection';
import { StatusNotice } from './components/StatusNotice';
import { downloadResponse, formatSize, getWorkspaceId, workspaceHeaders } from './utils/files';
import type { ReadyFile } from './utils/files';
import type { Notice } from './types';

export default function App() {
  const [files, setFiles] = useState<File[]>([]);
  const [mode, setMode] = useState('editable');
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState<Notice | null>(null);
  const [workspaceId] = useState(getWorkspaceId);
  const [readyFiles, setReadyFiles] = useState<ReadyFile[]>([]);

  const refreshReadyFiles = useCallback(async () => {
    const response = await fetch('/api/files', { headers: workspaceHeaders(workspaceId) });
    if (!response.ok) throw new Error('Could not load your saved files.');
    const result: { files: ReadyFile[] } = await response.json();
    setReadyFiles(result.files);
  }, [workspaceId]);

  useEffect(() => {
    void refreshReadyFiles().catch(() => setReadyFiles([]));
  }, [refreshReadyFiles]);

  const addFiles = useCallback((incoming: FileList | File[]) => {
    const list = Array.from(incoming);
    const accepted = list.filter((file) => file.name.toLowerCase().endsWith('.pdf'));
    if (accepted.length !== list.length) setNotice({ type: 'error', text: 'Only PDF files can be added to the merge list.' });
    setFiles((current) => [...current, ...accepted.filter((file) => !current.some((item) => item.name === file.name && item.size === file.size && item.lastModified === file.lastModified))]);
  }, []);

  const perform = async (label: string, request: () => Promise<Response>) => {
    setBusy(true);
    setNotice({ type: 'working', text: label });
    try {
      const response = await request();
      if (!response.ok) {
        const body: { detail?: string } = await response.json().catch(() => ({}));
        throw new Error(body.detail || 'The operation could not be completed.');
      }
      await refreshReadyFiles();
      setNotice({ type: 'success', text: 'Your file is ready below and will be kept for 7 days.' });
    } catch (error) {
      setNotice({ type: 'error', text: error instanceof Error ? error.message : 'Something went wrong. Please try again.' });
    } finally {
      setBusy(false);
    }
  };

  const merge = () => {
    const body = new FormData();
    files.forEach((file) => body.append('files', file));
    return perform('Merging your PDFs…', () => fetch('/api/merge', { method: 'POST', body, headers: workspaceHeaders(workspaceId) }));
  };

  const convertPdf = (file?: File) => {
    if (!file) return;
    const body = new FormData();
    body.append('file', file);
    body.append('mode', mode);
    void perform('Converting PDF to Word…', () => fetch('/api/pdf-to-word', { method: 'POST', body, headers: workspaceHeaders(workspaceId) }));
  };

  const convertWord = (file?: File) => {
    if (!file) return;
    const body = new FormData();
    body.append('file', file);
    void perform('Converting Word to PDF…', () => fetch('/api/word-to-pdf', { method: 'POST', body, headers: workspaceHeaders(workspaceId) }));
  };

  const downloadSavedFile = async (file: ReadyFile) => {
    try {
      await downloadResponse(await fetch(`/api/files/${file.id}`, { headers: workspaceHeaders(workspaceId) }), file.filename);
    } catch (error) {
      setNotice({ type: 'error', text: error instanceof Error ? error.message : 'Could not download this file.' });
      await refreshReadyFiles().catch(() => undefined);
    }
  };

  const removeSavedFile = async (file: ReadyFile) => {
    try {
      const response = await fetch(`/api/files/${file.id}`, { method: 'DELETE', headers: workspaceHeaders(workspaceId) });
      if (!response.ok) throw new Error('Could not remove this file.');
      await refreshReadyFiles();
    } catch (error) {
      setNotice({ type: 'error', text: error instanceof Error ? error.message : 'Could not remove this file.' });
    }
  };

  const moveFile = (index: number, delta: number) => setFiles((current) => {
    const target = index + delta;
    if (target < 0 || target >= current.length) return current;
    const next = [...current];
    [next[index], next[target]] = [next[target], next[index]];
    return next;
  });

  return <main className="mx-auto w-[min(100%_-_40px,930px)] max-[650px]:w-[min(100%_-_28px,930px)]"><BrandHeader /><Intro /><MergeSection files={files} busy={busy} onAdd={addFiles} onRemove={(index) => setFiles((current) => current.filter((_, item) => item !== index))} onMove={moveFile} onMerge={() => void merge()} /><ConversionSection mode={mode} busy={busy} onModeChange={setMode} onPdf={convertPdf} onWord={convertWord} /><section className="mt-[26px] rounded-[14px] border border-[#e8eaf0] bg-white p-[18px] shadow-[0_3px_12px_#28375e08]"><div className="flex items-center justify-between"><div><h2 className="m-0 font-[Manrope,sans-serif] text-base font-bold text-[#273145]">Ready to download</h2><p className="mt-1 mb-0 text-xs text-[#8a91a0]">Your files are kept here for 7 days.</p></div><button className="rounded-lg border border-[#dfe3eb] bg-white px-3 py-2 text-xs font-semibold text-[#4857a0] hover:bg-[#f7f8ff]" onClick={() => void refreshReadyFiles().catch(() => setNotice({ type: 'error', text: 'Could not refresh your saved files.' }))}>Refresh</button></div>{readyFiles.length === 0 ? <p className="mb-0 mt-5 rounded-lg bg-[#fafbfe] px-4 py-5 text-center text-xs text-[#8a91a0]">Files you merge or convert will appear here.</p> : <div className="mt-4 overflow-hidden rounded-[9px] border border-[#eceef2]">{readyFiles.map((file) => <div key={file.id} className="flex items-center gap-3 border-b border-[#f0f1f4] px-3 py-3 last:border-0"><span className="grid h-9 w-9 shrink-0 place-items-center rounded-[9px] bg-[#efefff] text-[#5957bb]"><FileType2 size={17} /></span><span className="min-w-0 flex-1 overflow-hidden text-ellipsis whitespace-nowrap text-xs font-semibold text-[#39445a]">{file.filename}<small className="mt-1 block font-normal text-[#969dab]">{formatSize(file.size)} · Expires {new Date(file.expiresAt).toLocaleDateString()}</small></span><button className="rounded-lg bg-[#344fbd] px-3 py-2 text-xs font-semibold text-white hover:bg-[#2943a9]" onClick={() => void downloadSavedFile(file)}>Download</button><button className="rounded-lg px-2 py-2 text-xs text-[#8f97a5] hover:bg-[#f1f2f6]" aria-label={`Delete ${file.filename}`} onClick={() => void removeSavedFile(file)}>Delete</button></div>)}</div>}</section><AppFooter /><StatusNotice notice={notice} onDismiss={() => setNotice(null)} />{busy && <div className="fixed inset-0 z-[4] flex items-center justify-center gap-2.5 bg-[#f7f8fa77] text-[13px] text-[#45558e] backdrop-blur-[1px]" aria-live="polite"><LoaderCircle className="animate-spin" size={18} /><span>{notice?.text}</span></div>}</main>;
}
