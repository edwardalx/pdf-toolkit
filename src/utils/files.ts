export function formatSize(bytes: number): string {
  return bytes < 1024 * 1024
    ? `${Math.max(1, Math.round(bytes / 1024))} KB`
    : `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

export type ReadyFile = {
  id: string;
  filename: string;
  size: number;
  createdAt: string;
  expiresAt: string;
};

export function getWorkspaceId(): string {
  const key = 'paperplane-workspace-id';
  let id = window.localStorage.getItem(key);
  if (!id) {
    id = window.crypto.randomUUID();
    window.localStorage.setItem(key, id);
  }
  return id;
}

export function workspaceHeaders(workspaceId: string): HeadersInit {
  return { 'X-Workspace-Id': workspaceId };
}

export async function downloadResponse(response: Response, fallbackName: string): Promise<void> {
  if (!response.ok) {
    let message = 'The operation could not be completed.';
    try {
      const body: { detail?: string } = await response.json();
      message = body.detail || message;
    } catch {
      // Keep the generic error when the response is not JSON.
    }
    throw new Error(message);
  }

  const blob = await response.blob();
  const disposition = response.headers.get('content-disposition') || '';
  const filename = disposition.match(/filename="?([^";]+)"?/i)?.[1] || fallbackName;
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}
