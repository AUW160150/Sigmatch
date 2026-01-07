import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { ClipboardList, Check, X, Clock } from 'lucide-react';

const dummyPatients = [
  { id: 'PT-001', decision: 'Matched', score: 4.2, status: 'pending' },
  { id: 'PT-002', decision: 'Not Matched', score: 2.1, status: 'pending' },
  { id: 'PT-003', decision: 'Matched', score: 4.8, status: 'approved' },
  { id: 'PT-004', decision: 'Matched', score: 3.5, status: 'rejected' },
];

export default function ReviewResults() {
  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-semibold">Manual Review Results</h1>
        <p className="text-muted-foreground">Review and approve/reject patient matches</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ClipboardList className="h-5 w-5 text-primary" />
            Patient Matches
          </CardTitle>
          <CardDescription>
            This feature is coming soon. You will be able to manually review and approve/reject patient matches here.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="rounded-lg border border-dashed border-border p-8 text-center mb-6">
            <Clock className="mx-auto h-12 w-12 text-muted-foreground/50 mb-4" />
            <h3 className="text-lg font-medium mb-2">Feature In Development</h3>
            <p className="text-muted-foreground max-w-md mx-auto">
              The manual review functionality is currently being developed. Below is a preview of how it will look.
            </p>
          </div>

          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Patient ID</TableHead>
                <TableHead>Decision</TableHead>
                <TableHead>Score</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {dummyPatients.map((patient) => (
                <TableRow key={patient.id}>
                  <TableCell className="font-medium">{patient.id}</TableCell>
                  <TableCell>
                    <Badge
                      variant={patient.decision === 'Matched' ? 'default' : 'secondary'}
                      className={patient.decision === 'Matched' ? 'bg-success' : ''}
                    >
                      {patient.decision}
                    </Badge>
                  </TableCell>
                  <TableCell>{patient.score.toFixed(1)}</TableCell>
                  <TableCell>
                    <Badge
                      variant="outline"
                      className={
                        patient.status === 'approved'
                          ? 'border-success text-success'
                          : patient.status === 'rejected'
                          ? 'border-destructive text-destructive'
                          : ''
                      }
                    >
                      {patient.status}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-2">
                      <Button variant="outline" size="sm" disabled>
                        <Check className="mr-1 h-3 w-3" />
                        Approve
                      </Button>
                      <Button variant="outline" size="sm" disabled>
                        <X className="mr-1 h-3 w-3" />
                        Reject
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
