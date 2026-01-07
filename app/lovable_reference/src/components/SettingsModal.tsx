import { useState, useEffect } from 'react';
import { Settings, Check, X, Loader2 } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useApi } from '@/contexts/ApiContext';
import { useToast } from '@/hooks/use-toast';

export function SettingsModal() {
  const { apiBase, setApiBase } = useApi();
  const [inputValue, setInputValue] = useState(apiBase);
  const [isOpen, setIsOpen] = useState(false);
  const [isTesting, setIsTesting] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'unknown' | 'connected' | 'disconnected'>('unknown');
  const { toast } = useToast();

  useEffect(() => {
    if (isOpen) {
      setInputValue(apiBase);
      setConnectionStatus('unknown');
    }
  }, [isOpen, apiBase]);

  const testConnection = async () => {
    setIsTesting(true);
    setConnectionStatus('unknown');
    try {
      const response = await fetch(`${inputValue}/api/config`, {
        method: 'GET',
        headers: { 'Accept': 'application/json' },
      });
      if (response.ok) {
        setConnectionStatus('connected');
        toast({ title: 'Connection successful', description: 'Backend API is reachable.' });
      } else {
        setConnectionStatus('disconnected');
        toast({ title: 'Connection failed', description: `Server returned ${response.status}`, variant: 'destructive' });
      }
    } catch (error) {
      setConnectionStatus('disconnected');
      toast({ title: 'Connection failed', description: 'Could not reach the backend API.', variant: 'destructive' });
    } finally {
      setIsTesting(false);
    }
  };

  const handleSave = () => {
    const trimmedUrl = inputValue.trim().replace(/\/$/, ''); // Remove trailing slash
    setApiBase(trimmedUrl);
    toast({ title: 'Settings saved', description: 'Backend API URL updated.' });
    setIsOpen(false);
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <button className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-sidebar-foreground/70 hover:bg-sidebar-accent/50 hover:text-sidebar-foreground transition-colors">
          <Settings className="h-4 w-4" />
          Settings
        </button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Settings</DialogTitle>
          <DialogDescription>
            Configure the backend API connection for Sigmatch.
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="api-url">Backend API URL</Label>
            <Input
              id="api-url"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="http://localhost:8000"
            />
          </div>

          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">Status:</span>
            {connectionStatus === 'unknown' && (
              <span className="text-sm text-muted-foreground">Not tested</span>
            )}
            {connectionStatus === 'connected' && (
              <span className="flex items-center gap-1 text-sm text-green-600">
                <Check className="h-4 w-4" />
                Connected
              </span>
            )}
            {connectionStatus === 'disconnected' && (
              <span className="flex items-center gap-1 text-sm text-destructive">
                <X className="h-4 w-4" />
                Disconnected
              </span>
            )}
          </div>

          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={testConnection}
              disabled={isTesting || !inputValue.trim()}
              className="flex-1"
            >
              {isTesting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Testing...
                </>
              ) : (
                'Test Connection'
              )}
            </Button>
            <Button
              onClick={handleSave}
              disabled={!inputValue.trim()}
              className="flex-1"
            >
              Save
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
