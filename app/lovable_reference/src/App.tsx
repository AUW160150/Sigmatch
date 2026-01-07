import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { MainLayout } from "./components/layout/MainLayout";
import { ApiProvider } from "./contexts/ApiContext";
import Configure from "./pages/Configure";
import AdjustPrompts from "./pages/AdjustPrompts";
import EvaluationCriteria from "./pages/EvaluationCriteria";
import ReviewResults from "./pages/ReviewResults";
import ResultsSummary from "./pages/ResultsSummary";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <ApiProvider>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            <Route element={<MainLayout />}>
              <Route path="/" element={<Configure />} />
              <Route path="/prompts" element={<AdjustPrompts />} />
              <Route path="/evaluation" element={<EvaluationCriteria />} />
              <Route path="/review" element={<ReviewResults />} />
              <Route path="/results" element={<ResultsSummary />} />
            </Route>
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </ApiProvider>
  </QueryClientProvider>
);

export default App;
