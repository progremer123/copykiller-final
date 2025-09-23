import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { FileUpload } from './FileUpload';
import { TextInput } from './TextInput';
import { ResultsDisplay } from './ResultsDisplay';
import { SearchHistory } from './SearchHistory';
export interface CheckResult {
  id: string;
  originalText: string;
  similarity: number;
  matches: Array<{
    text: string;
    source: string;
    similarity: number;
    startIndex: number;
    endIndex: number;
  }>;
  status: 'checking' | 'completed' | 'error';
  timestamp: Date;
}
const PlagiarismChecker = () => {
  const [results, setResults] = useState<CheckResult[]>([]);
  const [activeTab, setActiveTab] = useState('upload');
  const handleTextSubmit = async (text: string) => {
    const newCheck: CheckResult = {
      id: Date.now().toString(),
      originalText: text,
      similarity: 0,
      matches: [],
      status: 'checking',
      timestamp: new Date()
    };
    setResults(prev => [newCheck, ...prev]);
    setActiveTab('results');

    // Simulate API call to your FastAPI backend
    setTimeout(() => {
      setResults(prev => prev.map(result => result.id === newCheck.id ? {
        ...result,
        status: 'completed' as const,
        similarity: Math.random() * 100,
        matches: [{
          text: 'Sample matching text found in database',
          source: 'Academic Paper - Nature Journal 2023',
          similarity: 85,
          startIndex: 10,
          endIndex: 50
        }, {
          text: 'Another potential match detected',
          source: 'Research Database - IEEE',
          similarity: 72,
          startIndex: 100,
          endIndex: 140
        }]
      } : result));
    }, 3000);
  };
  const handleFileSubmit = async (file: File) => {
    // Convert file to text (you'll implement this based on file type)
    const text = await file.text();
    handleTextSubmit(text);
  };
  return <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <div className="text-center mb-8 bg-slate-50">
          <h1 className="text-4xl font-bold text-foreground mb-4">GPT 표절 검사기</h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            AI 기반 표절 검사로 학술 논문, 보고서, 에세이의 독창성을 확인하세요. 
            빠르고 정확한 결과를 제공합니다.
          </p>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-3 mb-8">
            <TabsTrigger value="upload">파일 업로드</TabsTrigger>
            <TabsTrigger value="text">텍스트 입력</TabsTrigger>
            <TabsTrigger value="results">결과 ({results.length})</TabsTrigger>
          </TabsList>

          <TabsContent value="upload" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  파일 업로드
                </CardTitle>
              </CardHeader>
              <CardContent>
                <FileUpload onFileSubmit={handleFileSubmit} />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="text" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>텍스트 직접 입력</CardTitle>
              </CardHeader>
              <CardContent>
                <TextInput onTextSubmit={handleTextSubmit} />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="results" className="space-y-6">
            <ResultsDisplay results={results} />
            <SearchHistory results={results.filter(r => r.status === 'completed')} />
          </TabsContent>
        </Tabs>
      </div>
    </div>;
};
export default PlagiarismChecker;