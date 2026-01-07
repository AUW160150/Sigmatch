import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { Spinner } from '@/components/ui/spinner';
import { getResultsSummary, getDownloadUrl } from '@/lib/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { Download, Users, UserCheck, UserX, Percent, BarChart3, AlertCircle } from 'lucide-react';

interface ResultsSummary {
  has_results: boolean;
  cohort_name: string;
  total_patients: number;
  matched_count: number;
  not_matched_count: number;
  match_percentage: number;
  score_distribution: Record<string, number>;
}

export default function ResultsSummary() {
  const { toast } = useToast();
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState<ResultsSummary | null>(null);

  useEffect(() => {
    async function loadSummary() {
      try {
        const data = await getResultsSummary();
        setSummary(data);
      } catch (error) {
        toast({ title: 'Error loading results', description: String(error), variant: 'destructive' });
      } finally {
        setLoading(false);
      }
    }
    loadSummary();
  }, [toast]);

  if (loading) {
    return (
      <div className="flex h-[50vh] items-center justify-center">
        <Spinner size="lg" />
      </div>
    );
  }

  if (!summary?.has_results) {
    return (
      <div className="space-y-6 animate-fade-in">
        <div>
          <h1 className="text-2xl font-semibold">Results Summary</h1>
          <p className="text-muted-foreground">View matching results and statistics</p>
        </div>

        <Card>
          <CardContent className="flex flex-col items-center justify-center py-16">
            <AlertCircle className="h-16 w-16 text-muted-foreground/50 mb-4" />
            <h3 className="text-lg font-medium mb-2">No Results Available</h3>
            <p className="text-muted-foreground text-center max-w-md mb-6">
              Run the pipeline to generate matching results. Results will appear here once processing is complete.
            </p>
            <Button variant="outline" disabled>
              <Download className="mr-2 h-4 w-4" />
              Download Results (CSV)
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const chartData = Object.entries(summary.score_distribution).map(([score, count]) => ({
    score: `Score ${score}`,
    count,
    fill: `hsl(var(--chart-${score}))`,
  }));

  const stats = [
    { label: 'Total Patients', value: summary.total_patients, icon: Users, color: 'text-primary' },
    { label: 'Matched', value: summary.matched_count, icon: UserCheck, color: 'text-success' },
    { label: 'Not Matched', value: summary.not_matched_count, icon: UserX, color: 'text-destructive' },
    { label: 'Match Rate', value: `${summary.match_percentage.toFixed(1)}%`, icon: Percent, color: 'text-primary' },
  ];

  const handleDownload = () => {
    window.open(getDownloadUrl(), '_blank');
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Results Summary</h1>
          <p className="text-muted-foreground">
            Cohort: <span className="font-medium text-foreground">{summary.cohort_name}</span>
          </p>
        </div>
        <Button onClick={handleDownload}>
          <Download className="mr-2 h-4 w-4" />
          Download Results (CSV)
        </Button>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.label} className="stat-card">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">{stat.label}</p>
                  <p className={`text-3xl font-bold ${stat.color}`}>{stat.value}</p>
                </div>
                <div className={`rounded-full p-3 bg-muted ${stat.color}`}>
                  <stat.icon className="h-6 w-6" />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Chart */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-primary" />
            Score Distribution
          </CardTitle>
          <CardDescription>Distribution of matching scores across all patients</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis
                  dataKey="score"
                  className="text-xs fill-muted-foreground"
                  tick={{ fill: 'hsl(var(--muted-foreground))' }}
                />
                <YAxis
                  className="text-xs fill-muted-foreground"
                  tick={{ fill: 'hsl(var(--muted-foreground))' }}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'hsl(var(--card))',
                    border: '1px solid hsl(var(--border))',
                    borderRadius: 'var(--radius)',
                  }}
                  labelStyle={{ color: 'hsl(var(--foreground))' }}
                />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={`hsl(var(--chart-${index + 1}))`} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
