import { FileText } from 'lucide-react';

export function AppFooter() {
  return <footer className="flex justify-between gap-5 py-5 pb-[26px] text-[10px] text-[#9da3ae] max-[650px]:flex-col max-[650px]:gap-2"><span>Files are stored on your server and automatically deleted after 7 days.</span><span className="flex items-center gap-[5px] whitespace-nowrap max-[650px]:hidden">Made for documents <FileText size={14} /></span></footer>;
}
