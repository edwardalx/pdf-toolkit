import { Check, LoaderCircle, X } from 'lucide-react';
import type { Notice } from '../types';

export function StatusNotice({ notice, onDismiss }: { notice: Notice | null; onDismiss: () => void }) {
  if (!notice) return null;
  const icon = notice.type === 'working' ? <LoaderCircle className="animate-spin" size={17} /> : notice.type === 'success' ? <Check size={17} /> : <X size={17} />;
  return <div className={`fixed bottom-6 left-1/2 z-[5] flex max-w-[min(90vw,520px)] -translate-x-1/2 items-center gap-[9px] rounded-[9px] border border-[#e5e8ee] bg-white px-[13px] py-[11px] text-xs text-[#556176] shadow-[0_8px_25px_#17234018] ${notice.type === 'success' ? 'text-[#3c7659]' : notice.type === 'error' ? 'text-[#a94d4d]' : ''}`} role="status">{icon}<span>{notice.text}</span>{notice.type !== 'working' && <button className="ml-2 grid place-items-center rounded-[5px] p-[5px] text-[#8f97a5] hover:bg-[#f1f2f6]" onClick={onDismiss} aria-label="Dismiss"><X size={15} /></button>}</div>;
}
