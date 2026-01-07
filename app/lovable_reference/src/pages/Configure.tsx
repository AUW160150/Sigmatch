import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Checkbox } from '@/components/ui/checkbox';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { useToast } from '@/hooks/use-toast';
import { Spinner } from '@/components/ui/spinner';
import { getTrials, getConfig, updateConfig, runPipeline, saveSnapshot, uploadTrial, createTrial, getCohorts, assembleCohort } from '@/lib/api';
import { Upload, ChevronDown, Play, Save, Copy, Check, FileText, Plus, X, Users, Search } from 'lucide-react';

interface Trial {
  filename: string;
  title: string;
  _id: string;
}

interface Cohort {
  filename: string;
  name: string;
}

export default function Configure() {
  const { toast } = useToast();
  const [loading, setLoading] = useState(true);
  const [trials, setTrials] = useState<Trial[]>([]);
  const [selectedTrial, setSelectedTrial] = useState('');
  const [cohortType, setCohortType] = useState('dummy_cohort1');
  const [customPath, setCustomPath] = useState('');
  const [cohortName, setCohortName] = useState('');
  const [pipelineSteps, setPipelineSteps] = useState({
    ocr: false,
    llmSummarization: true,
    patientMatching: true,
    evaluation: false,
  });
  const [isRunning, setIsRunning] = useState(false);
  const [command, setCommand] = useState('');
  const [copied, setCopied] = useState(false);
  const [freeTextOpen, setFreeTextOpen] = useState(false);
  const [newTrialTitle, setNewTrialTitle] = useState('');
  const [newTrialDescription, setNewTrialDescription] = useState('');
  const [savingTrial, setSavingTrial] = useState(false);

  // Assemble Cohort state
  const [cohortSources, setCohortSources] = useState<Cohort[]>([]);
  const [assembleCriteria, setAssembleCriteria] = useState<string[]>(['']);
  const [selectedCohortSource, setSelectedCohortSource] = useState('');
  const [maxPatients, setMaxPatients] = useState('50');
  const [isAssembling, setIsAssembling] = useState(false);
  const [assembleResults, setAssembleResults] = useState<{ matched_count: number; patient_ids_list: string[] } | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const [trialsData, configData] = await Promise.all([
          getTrials(),
          getConfig(),
        ]);
        setTrials(trialsData?.trials || []);
        
        // Load cohorts separately to handle API not existing yet
        try {
          const cohortsData = await getCohorts();
          setCohortSources(cohortsData?.cohorts || []);
        } catch {
          // Cohorts API may not be available yet
          setCohortSources([]);
        }
        
        if (configData?.config) {
          setCohortName(configData.config.cohortName || '');
          if (configData.config.trial_file_config_path) {
            const trial = (trialsData?.trials || []).find(
              t => t.filename === configData.config.trial_file_config_path.split('/').pop()
            );
            if (trial) setSelectedTrial(trial.filename);
          }
        }
      } catch (error) {
        toast({ title: 'Error loading data', description: String(error), variant: 'destructive' });
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [toast]);

  const handleTrialSelect = async (filename: string) => {
    setSelectedTrial(filename);
    try {
      await updateConfig({ trial_file_config_path: `config_files/trial_files/${filename}` });
      toast({ title: 'Trial updated', description: 'Configuration saved successfully.' });
    } catch (error) {
      toast({ title: 'Error', description: String(error), variant: 'destructive' });
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      await uploadTrial(file);
      const trialsData = await getTrials();
      setTrials(trialsData.trials);
      toast({ title: 'Trial uploaded', description: 'File uploaded successfully.' });
    } catch (error) {
      toast({ title: 'Upload failed', description: String(error), variant: 'destructive' });
    }
  };

  const handleSaveTrial = async () => {
    if (!newTrialTitle.trim() || !newTrialDescription.trim()) {
      toast({ title: 'Missing fields', description: 'Please fill in both title and description.', variant: 'destructive' });
      return;
    }
    setSavingTrial(true);
    try {
      await createTrial(newTrialTitle, newTrialDescription);
      const trialsData = await getTrials();
      setTrials(trialsData.trials);
      setNewTrialTitle('');
      setNewTrialDescription('');
      setFreeTextOpen(false);
      toast({ title: 'Trial created', description: 'New trial saved successfully.' });
    } catch (error) {
      toast({ title: 'Error', description: String(error), variant: 'destructive' });
    } finally {
      setSavingTrial(false);
    }
  };

  const handleCohortChange = async (value: string) => {
    setCohortType(value);
    if (value !== 'custom') {
      try {
        await updateConfig({
          patients_file_path: `config_files/pipeline_json_files/${value}.json`,
          cohortName: cohortName,
        });
      } catch (error) {
        toast({ title: 'Error', description: String(error), variant: 'destructive' });
      }
    }
  };

  const handleRunPipeline = async () => {
    setIsRunning(true);
    setCommand('');
    try {
      const result = await runPipeline({
        config_path: 'config_files/overall_config_settings/active_data_config.json',
        run_ocr: pipelineSteps.ocr,
        do_llm_summarization: pipelineSteps.llmSummarization,
        do_patient_matching: pipelineSteps.patientMatching,
        do_evaluation: pipelineSteps.evaluation,
      });
      setCommand(result.command);
      toast({ title: 'Pipeline started', description: 'The matching pipeline is now running.' });
    } catch (error) {
      toast({ title: 'Pipeline failed', description: String(error), variant: 'destructive' });
    } finally {
      setIsRunning(false);
    }
  };

  const handleSaveSnapshot = async () => {
    try {
      const result = await saveSnapshot();
      toast({ title: 'Snapshot saved', description: `Saved to: ${result.snapshot_directory}` });
    } catch (error) {
      toast({ title: 'Error', description: String(error), variant: 'destructive' });
    }
  };

  const copyCommand = () => {
    navigator.clipboard.writeText(command);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Assemble Cohort handlers
  const addCriterion = () => {
    setAssembleCriteria([...assembleCriteria, '']);
  };

  const removeCriterion = (index: number) => {
    if (assembleCriteria.length > 1) {
      setAssembleCriteria(assembleCriteria.filter((_, i) => i !== index));
    }
  };

  const updateCriterion = (index: number, value: string) => {
    const updated = [...assembleCriteria];
    updated[index] = value;
    setAssembleCriteria(updated);
  };

  const handleAssembleCohort = async () => {
    const validCriteria = assembleCriteria.filter(c => c.trim() !== '');
    if (validCriteria.length === 0) {
      toast({ title: 'No criteria', description: 'Please add at least one criterion.', variant: 'destructive' });
      return;
    }
    if (!selectedCohortSource) {
      toast({ title: 'No cohort source', description: 'Please select a cohort source.', variant: 'destructive' });
      return;
    }

    setIsAssembling(true);
    setAssembleResults(null);
    try {
      const result = await assembleCohort({
        criteria: validCriteria,
        max_patients: parseInt(maxPatients),
        cohort_source: selectedCohortSource,
      });
      setAssembleResults(result);
      toast({ title: 'Cohort assembled', description: `Found ${result.matched_count} patients.` });
    } catch (error) {
      toast({ title: 'Assembly failed', description: String(error), variant: 'destructive' });
    } finally {
      setIsAssembling(false);
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
        <h1 className="text-2xl font-semibold">Configure Pipeline</h1>
        <p className="text-muted-foreground">Set up your clinical trial matching parameters</p>
      </div>

      {/* Assemble Cohort Section - Full Width */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5 text-primary" />
            Assemble Cohort
          </CardTitle>
          <CardDescription>Define criteria to identify matching patients from a cohort source</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-6 lg:grid-cols-2">
            {/* Left: Criteria inputs */}
            <div className="space-y-4">
              <div className="space-y-2">
                <Label>Patient Criteria</Label>
                <div className="space-y-2">
                  {assembleCriteria.map((criterion, index) => (
                    <div key={index} className="flex gap-2">
                      <Input
                        value={criterion}
                        onChange={(e) => updateCriterion(index, e.target.value)}
                        placeholder="e.g., patients who received gemcitabine"
                        className="flex-1"
                      />
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => removeCriterion(index)}
                        disabled={assembleCriteria.length === 1}
                        className="shrink-0"
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                </div>
                <Button variant="outline" size="sm" onClick={addCriterion} className="mt-2">
                  <Plus className="mr-2 h-4 w-4" />
                  Add Criterion
                </Button>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-2">
                  <Label>Cohort Source</Label>
                  <Select value={selectedCohortSource} onValueChange={setSelectedCohortSource}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select source..." />
                    </SelectTrigger>
                    <SelectContent>
                      {cohortSources.map((cohort) => (
                        <SelectItem key={cohort.filename} value={cohort.filename}>
                          {cohort.name || cohort.filename}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Max Patients</Label>
                  <Select value={maxPatients} onValueChange={setMaxPatients}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="25">25</SelectItem>
                      <SelectItem value="50">50</SelectItem>
                      <SelectItem value="100">100</SelectItem>
                      <SelectItem value="250">250</SelectItem>
                      <SelectItem value="500">500</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <Button onClick={handleAssembleCohort} disabled={isAssembling} className="w-full sm:w-auto">
                {isAssembling ? <Spinner size="sm" className="mr-2" /> : <Search className="mr-2 h-4 w-4" />}
                Identify Patients
              </Button>
            </div>

            {/* Right: Results */}
            <div className="space-y-2">
              <Label>Results</Label>
              <div className="rounded-lg border bg-muted/50 p-4 min-h-[200px]">
                {assembleResults ? (
                  <div className="space-y-2">
                    {assembleResults.matched_count > 0 ? (
                      <>
                        <p className="font-medium text-foreground">
                          Found <span className="text-primary">{assembleResults.matched_count}</span> patients:
                        </p>
                        <div className="flex flex-wrap gap-2">
                          {(assembleResults.patient_ids_list || []).map((id) => (
                            <span
                              key={id}
                              className="inline-flex items-center rounded-md bg-primary/10 px-2.5 py-1 text-sm font-medium text-primary ring-1 ring-inset ring-primary/20"
                            >
                              {id}
                            </span>
                          ))}
                        </div>
                      </>
                    ) : (
                      <p className="text-yellow-600">No patients found matching all criteria.</p>
                    )}
                  </div>
                ) : (
                  <p className="text-muted-foreground text-sm">
                    Enter criteria and click "Identify Patients" to find matching patients.
                  </p>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Trial Selection */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-primary" />
              Trial Selection
            </CardTitle>
            <CardDescription>Choose or upload a clinical trial</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Select Trial</Label>
              <Select value={selectedTrial} onValueChange={handleTrialSelect}>
                <SelectTrigger>
                  <SelectValue placeholder="Choose a trial..." />
                </SelectTrigger>
                <SelectContent>
                  {trials.map((trial) => (
                    <SelectItem key={trial._id} value={trial.filename}>
                      {trial.title}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <Button variant="outline" asChild className="w-full">
              <label className="cursor-pointer">
                <Upload className="mr-2 h-4 w-4" />
                Upload JSON
                <input type="file" accept=".json" className="hidden" onChange={handleFileUpload} />
              </label>
            </Button>

            <Collapsible open={freeTextOpen} onOpenChange={setFreeTextOpen}>
              <CollapsibleTrigger asChild>
                <Button variant="ghost" className="w-full justify-between">
                  Create from free text
                  <ChevronDown className={`h-4 w-4 transition-transform ${freeTextOpen ? 'rotate-180' : ''}`} />
                </Button>
              </CollapsibleTrigger>
              <CollapsibleContent className="space-y-3 pt-3">
                <div className="space-y-2">
                  <Label>Trial Title</Label>
                  <Input
                    value={newTrialTitle}
                    onChange={(e) => setNewTrialTitle(e.target.value)}
                    placeholder="Enter trial title..."
                  />
                </div>
                <div className="space-y-2">
                  <Label>Trial Description (Full Text)</Label>
                  <Textarea
                    value={newTrialDescription}
                    onChange={(e) => setNewTrialDescription(e.target.value)}
                    placeholder="Enter the full trial description..."
                    rows={6}
                  />
                </div>
                <Button onClick={handleSaveTrial} disabled={savingTrial}>
                  {savingTrial ? <Spinner size="sm" className="mr-2" /> : <Save className="mr-2 h-4 w-4" />}
                  Save Trial
                </Button>
              </CollapsibleContent>
            </Collapsible>
          </CardContent>
        </Card>

        {/* Cohort Selection */}
        <Card>
          <CardHeader>
            <CardTitle>Cohort Selection</CardTitle>
            <CardDescription>Select patient cohort for matching</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <RadioGroup value={cohortType} onValueChange={handleCohortChange}>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="dummy_cohort1" id="cohort1" />
                <Label htmlFor="cohort1">dummy_cohort1</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="dummy_cohort2" id="cohort2" />
                <Label htmlFor="cohort2">dummy_cohort2</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="custom" id="custom" />
                <Label htmlFor="custom">Custom path</Label>
              </div>
            </RadioGroup>

            {cohortType === 'custom' && (
              <div className="space-y-2">
                <Label>Custom Path</Label>
                <Input
                  value={customPath}
                  onChange={(e) => setCustomPath(e.target.value)}
                  placeholder="config_files/pipeline_json_files/..."
                />
              </div>
            )}

            <div className="space-y-2">
              <Label>Cohort Name</Label>
              <Input
                value={cohortName}
                onChange={(e) => setCohortName(e.target.value)}
                placeholder="Enter cohort name..."
              />
            </div>
          </CardContent>
        </Card>

        {/* Pipeline Steps */}
        <Card>
          <CardHeader>
            <CardTitle>Pipeline Steps</CardTitle>
            <CardDescription>Select which steps to run</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center space-x-2">
              <Checkbox
                id="ocr"
                checked={pipelineSteps.ocr}
                onCheckedChange={(checked) => setPipelineSteps((prev) => ({ ...prev, ocr: !!checked }))}
              />
              <Label htmlFor="ocr">OCR</Label>
            </div>
            <div className="flex items-center space-x-2">
              <Checkbox
                id="llm"
                checked={pipelineSteps.llmSummarization}
                onCheckedChange={(checked) => setPipelineSteps((prev) => ({ ...prev, llmSummarization: !!checked }))}
              />
              <Label htmlFor="llm">LLM Summarization</Label>
            </div>
            <div className="flex items-center space-x-2">
              <Checkbox
                id="matching"
                checked={pipelineSteps.patientMatching}
                onCheckedChange={(checked) => setPipelineSteps((prev) => ({ ...prev, patientMatching: !!checked }))}
              />
              <Label htmlFor="matching">Patient Matching</Label>
            </div>
            <div className="flex items-center space-x-2">
              <Checkbox
                id="eval"
                checked={pipelineSteps.evaluation}
                onCheckedChange={(checked) => setPipelineSteps((prev) => ({ ...prev, evaluation: !!checked }))}
              />
              <Label htmlFor="eval">Evaluation</Label>
            </div>
          </CardContent>
        </Card>

        {/* Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Actions</CardTitle>
            <CardDescription>Run pipeline or save configuration</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button className="w-full" size="lg" onClick={handleRunPipeline} disabled={isRunning}>
              {isRunning ? <Spinner size="sm" className="mr-2" /> : <Play className="mr-2 h-4 w-4" />}
              Run Pipeline
            </Button>
            <Button variant="secondary" className="w-full" onClick={handleSaveSnapshot}>
              <Save className="mr-2 h-4 w-4" />
              Save Snapshot
            </Button>

            {command && (
              <div className="space-y-2">
                <Label>Generated Command</Label>
                <div className="relative">
                  <pre className="code-block text-xs">{command}</pre>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="absolute right-2 top-2"
                    onClick={copyCommand}
                  >
                    {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
