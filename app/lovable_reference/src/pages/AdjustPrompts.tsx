import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { useToast } from '@/hooks/use-toast';
import { Spinner } from '@/components/ui/spinner';
import { getPrompts, updatePrompt, saveAllPrompts } from '@/lib/api';
import { Save, Check, Bot } from 'lucide-react';

interface AgentPrompt {
  system_prompt: string;
  main_prompt: string;
  skip: boolean;
}

const agentLabels: Record<string, string> = {
  final_decision_agent: 'Final Decision Agent',
  eligibility_checker_agent: 'Eligibility Checker Agent',
  trial_analyzer_agent: 'Trial Analyzer Agent',
  patient_analyzer_agent: 'Patient Analyzer Agent',
  patient_record_summarize: 'Patient Record Summarizer',
  extract_features: 'Feature Extractor',
};

export default function AdjustPrompts() {
  const { toast } = useToast();
  const [loading, setLoading] = useState(true);
  const [prompts, setPrompts] = useState<Record<string, AgentPrompt>>({});
  const [saving, setSaving] = useState<string | null>(null);
  const [savingAll, setSavingAll] = useState(false);

  useEffect(() => {
    async function loadPrompts() {
      try {
        const data = await getPrompts();
        setPrompts(data.prompts);
      } catch (error) {
        toast({ title: 'Error loading prompts', description: String(error), variant: 'destructive' });
      } finally {
        setLoading(false);
      }
    }
    loadPrompts();
  }, [toast]);

  const handleUpdatePrompt = (agentName: string, field: keyof AgentPrompt, value: string | boolean) => {
    setPrompts((prev) => ({
      ...prev,
      [agentName]: {
        ...prev[agentName],
        [field]: value,
      },
    }));
  };

  const handleSaveAgent = async (agentName: string) => {
    setSaving(agentName);
    try {
      await updatePrompt(agentName, prompts[agentName]);
      toast({ title: 'Saved', description: `${agentLabels[agentName]} updated successfully.` });
    } catch (error) {
      toast({ title: 'Error', description: String(error), variant: 'destructive' });
    } finally {
      setSaving(null);
    }
  };

  const handleSaveAll = async () => {
    setSavingAll(true);
    try {
      await saveAllPrompts();
      toast({ title: 'All prompts saved', description: 'Prompts versioned and saved successfully.' });
    } catch (error) {
      toast({ title: 'Error', description: String(error), variant: 'destructive' });
    } finally {
      setSavingAll(false);
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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Adjust Prompts</h1>
          <p className="text-muted-foreground">Configure AI agent system and main prompts</p>
        </div>
        <Button onClick={handleSaveAll} disabled={savingAll}>
          {savingAll ? <Spinner size="sm" className="mr-2" /> : <Save className="mr-2 h-4 w-4" />}
          Save All Prompts
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bot className="h-5 w-5 text-primary" />
            Agent Prompts
          </CardTitle>
          <CardDescription>Edit system and main prompts for each AI agent</CardDescription>
        </CardHeader>
        <CardContent>
          <Accordion type="single" collapsible className="w-full">
            {Object.entries(prompts).map(([agentName, prompt]) => (
              <AccordionItem key={agentName} value={agentName}>
                <AccordionTrigger className="hover:no-underline">
                  <div className="flex items-center gap-3">
                    <span className="font-medium">{agentLabels[agentName] || agentName}</span>
                    {prompt.skip && (
                      <span className="rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground">
                        Skipped
                      </span>
                    )}
                  </div>
                </AccordionTrigger>
                <AccordionContent className="space-y-4 pt-4">
                  <div className="flex items-center justify-between rounded-lg border border-border bg-muted/50 p-3">
                    <div>
                      <Label htmlFor={`${agentName}-skip`} className="font-medium">
                        Skip this prompt
                      </Label>
                      <p className="text-xs text-muted-foreground">
                        Disable this agent in the pipeline
                      </p>
                    </div>
                    <Switch
                      id={`${agentName}-skip`}
                      checked={prompt.skip}
                      onCheckedChange={(checked) => handleUpdatePrompt(agentName, 'skip', checked)}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor={`${agentName}-system`}>System Prompt</Label>
                    <Textarea
                      id={`${agentName}-system`}
                      value={prompt.system_prompt}
                      onChange={(e) => handleUpdatePrompt(agentName, 'system_prompt', e.target.value)}
                      rows={6}
                      className="font-mono text-sm"
                      placeholder="Enter system prompt..."
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor={`${agentName}-main`}>Main Prompt</Label>
                    <Textarea
                      id={`${agentName}-main`}
                      value={prompt.main_prompt}
                      onChange={(e) => handleUpdatePrompt(agentName, 'main_prompt', e.target.value)}
                      rows={8}
                      className="font-mono text-sm"
                      placeholder="Enter main prompt..."
                    />
                  </div>

                  <Button onClick={() => handleSaveAgent(agentName)} disabled={saving === agentName}>
                    {saving === agentName ? (
                      <Spinner size="sm" className="mr-2" />
                    ) : (
                      <Check className="mr-2 h-4 w-4" />
                    )}
                    Save {agentLabels[agentName] || agentName}
                  </Button>
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </CardContent>
      </Card>
    </div>
  );
}
