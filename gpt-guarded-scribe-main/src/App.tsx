import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import NotFound from "./pages/NotFound";
import LoginPage from "./pages/login";
import PremiumPage from "./pages/Premium";
import MyPage from "./pages/MyPage";
import AICrawlingPage from "./pages/AICrawling";
import AIPlagiarismAvoidancePage from "./pages/AIPlagiarismAvoidance";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Index />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/premium" element={<PremiumPage />} />
          <Route path="/mypage" element={<MyPage />} />
          <Route path="/ai-crawling" element={<AICrawlingPage />} />
          <Route path="/ai-plagiarism-avoidance" element={<AIPlagiarismAvoidancePage />} />
          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;