import { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useToast } from '@/hooks/use-toast';
import { Spinner } from '@/components/ui/spinner';
import { getChatHistory, sendChatMessage, saveCriteria } from '@/lib/api';
import { Send, Save, MessageSquare, User, Bot } from 'lucide-react';
import { cn } from '@/lib/utils';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export default function EvaluationCriteria() {
  const { toast } = useToast();
  const [loading, setLoading] = useState(true);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const [criteria, setCriteria] = useState('');
  const [savingCriteria, setSavingCriteria] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    async function loadHistory() {
      try {
        const data = await getChatHistory();
        setMessages(data.messages || []);
      } catch (error) {
        // If API fails, start with empty history
        setMessages([]);
      } finally {
        setLoading(false);
      }
    }
    loadHistory();
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || sending) return;
    
    const userMessage = input.trim();
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
    setSending(true);

    try {
      const response = await sendChatMessage(userMessage);
      setMessages((prev) => [...prev, { role: 'assistant', content: response.message.content }]);
    } catch (error) {
      // Fallback echo response
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: `I received your message: "${userMessage}". How can I help you refine the evaluation criteria?` },
      ]);
    } finally {
      setSending(false);
    }
  };

  const handleSaveCriteria = async () => {
    if (!criteria.trim()) {
      toast({ title: 'Empty criteria', description: 'Please enter evaluation criteria.', variant: 'destructive' });
      return;
    }
    setSavingCriteria(true);
    try {
      await saveCriteria(criteria);
      toast({ title: 'Criteria saved', description: 'Evaluation criteria saved successfully.' });
    } catch (error) {
      toast({ title: 'Error', description: String(error), variant: 'destructive' });
    } finally {
      setSavingCriteria(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (loading) {
    return (
      <div className="flex h-[50vh] items-center justify-center">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-semibold">Evaluation Criteria</h1>
        <p className="text-muted-foreground">Configure criteria through conversation</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Chat Interface */}
        <Card className="flex flex-col">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MessageSquare className="h-5 w-5 text-primary" />
              Chat
            </CardTitle>
            <CardDescription>Discuss and refine evaluation criteria</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-1 flex-col">
            <ScrollArea className="flex-1 pr-4" style={{ height: '400px' }} ref={scrollRef}>
              <div className="space-y-4">
                {messages.length === 0 ? (
                  <div className="flex h-full items-center justify-center py-12 text-center">
                    <div className="text-muted-foreground">
                      <MessageSquare className="mx-auto mb-2 h-8 w-8" />
                      <p>No messages yet. Start the conversation!</p>
                    </div>
                  </div>
                ) : (
                  messages.map((msg, idx) => (
                    <div
                      key={idx}
                      className={cn(
                        'flex gap-3',
                        msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'
                      )}
                    >
                      <div
                        className={cn(
                          'flex h-8 w-8 shrink-0 items-center justify-center rounded-full',
                          msg.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted'
                        )}
                      >
                        {msg.role === 'user' ? (
                          <User className="h-4 w-4" />
                        ) : (
                          <Bot className="h-4 w-4" />
                        )}
                      </div>
                      <div
                        className={cn(
                          'max-w-[80%] rounded-lg px-4 py-2',
                          msg.role === 'user'
                            ? 'bg-primary text-primary-foreground'
                            : 'bg-muted text-muted-foreground'
                        )}
                      >
                        <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                      </div>
                    </div>
                  ))
                )}
                {sending && (
                  <div className="flex gap-3">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-muted">
                      <Spinner size="sm" />
                    </div>
                    <div className="rounded-lg bg-muted px-4 py-2">
                      <p className="text-sm text-muted-foreground">Typing...</p>
                    </div>
                  </div>
                )}
              </div>
            </ScrollArea>

            <div className="mt-4 flex gap-2">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Type your message..."
                disabled={sending}
              />
              <Button onClick={handleSend} disabled={sending || !input.trim()}>
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Criteria Editor */}
        <Card>
          <CardHeader>
            <CardTitle>Final Evaluation Criteria</CardTitle>
            <CardDescription>Enter the final criteria for patient matching evaluation</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="criteria">Evaluation Criteria</Label>
              <Textarea
                id="criteria"
                value={criteria}
                onChange={(e) => setCriteria(e.target.value)}
                placeholder="Enter your evaluation criteria here..."
                rows={16}
              />
            </div>
            <Button onClick={handleSaveCriteria} disabled={savingCriteria} className="w-full">
              {savingCriteria ? <Spinner size="sm" className="mr-2" /> : <Save className="mr-2 h-4 w-4" />}
              Save Criteria
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
