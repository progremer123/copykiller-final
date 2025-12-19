import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { 
  Bot, 
  Globe, 
  Search, 
  Database, 
  CheckCircle, 
  XCircle, 
  Loader2,
  BarChart3,
  Download,
  Zap,
  Sparkles
} from 'lucide-react';

interface CrawlResult {
  query: string;
  status: string;
  collected: number;
  saved: number;
  sources: string[];
  error?: string;
}

interface BatchCrawlResponse {
  success: boolean;
  batch_summary: {
    total_queries: number;
    successful: number;
    failed: number;
    total_collected: number;
    total_saved: number;
    success_rate: string;
  };
  results: CrawlResult[];
  message: string;
}

interface SingleCrawlResponse {
  success: boolean;
  query: string;
  crawling_result: {
    total_crawled: number;
    saved_count: number;
    sources_used: string[];
  };
  summary: {
    total_collected: number;
    successfully_saved: number;
    sources_used: string[];
    coverage_ratio: string;
  };
  message: string;
}

const AICrawlingManager: React.FC = () => {
  const [singleQuery, setSingleQuery] = useState('');
  const [batchQueries, setBatchQueries] = useState('');
  const [numResults, setNumResults] = useState(15);
  const [resultsPerQuery, setResultsPerQuery] = useState(10);
  
  // AI 지식 생성 상태
  const [aiTopic, setAiTopic] = useState('');
  const [aiNumArticles, setAiNumArticles] = useState(5);
  const [aiTopics, setAiTopics] = useState('');
  const [aiArticlesPerTopic, setAiArticlesPerTopic] = useState(3);
  
  const [loading, setLoading] = useState(false);
  const [batchLoading, setBatchLoading] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiBatchLoading, setAiBatchLoading] = useState(false);
  
  const [singleResult, setSingleResult] = useState<SingleCrawlResponse | null>(null);
  const [batchResult, setBatchResult] = useState<BatchCrawlResponse | null>(null);
  const [aiResult, setAiResult] = useState<any>(null);
  const [aiBatchResult, setAiBatchResult] = useState<any>(null);
  const [sources, setSources] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [aiCapabilities, setAiCapabilities] = useState<any>(null);

  // API Base URL
  const API_BASE = 'http://localhost:8006/api';

  // 단일 AI 크롤링
  const handleSingleCrawl = async () => {
    if (!singleQuery.trim()) {
      alert('검색어를 입력해주세요.');
      return;
    }

    setLoading(true);
    setSingleResult(null);

    try {
      const response = await fetch(`${API_BASE}/crawl/ai-enhanced`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          query: singleQuery,
          num_results: numResults.toString()
        }),
      });

      if (response.ok) {
        const data: SingleCrawlResponse = await response.json();
        setSingleResult(data);
      } else {
        const error = await response.text();
        alert(`크롤링 실패: ${error}`);
      }
    } catch (error) {
      console.error('단일 크롤링 오류:', error);
      alert('크롤링 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 배치 AI 크롤링
  const handleBatchCrawl = async () => {
    const queries = batchQueries.trim().split('\n').filter(q => q.trim());
    
    if (queries.length === 0) {
      alert('최소 1개 이상의 검색어를 입력해주세요.');
      return;
    }

    if (queries.length > 10) {
      alert('한 번에 최대 10개까지만 처리 가능합니다.');
      return;
    }

    setBatchLoading(true);
    setBatchResult(null);

    try {
      const response = await fetch(`${API_BASE}/crawl/batch`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          queries: queries,
          results_per_query: resultsPerQuery
        }),
      });

      if (response.ok) {
        const data: BatchCrawlResponse = await response.json();
        setBatchResult(data);
      } else {
        const error = await response.text();
        alert(`배치 크롤링 실패: ${error}`);
      }
    } catch (error) {
      console.error('배치 크롤링 오류:', error);
      alert('배치 크롤링 중 오류가 발생했습니다.');
    } finally {
      setBatchLoading(false);
    }
  };

  // 크롤링 소스 목록 조회
  const loadSources = async () => {
    try {
      const response = await fetch(`${API_BASE}/crawl/sources`);
      if (response.ok) {
        const data = await response.json();
        setSources(data.sources || []);
      }
    } catch (error) {
      console.error('소스 목록 로딩 오류:', error);
    }
  };

  // 통계 조회 (AI 지식 통계 포함)
  const loadStats = async () => {
    try {
      const [crawlResponse, aiResponse] = await Promise.all([
        fetch(`${API_BASE}/crawl/stats`),
        fetch(`${API_BASE}/ai-knowledge/stats`)
      ]);
      
      let combinedStats = {};
      
      if (crawlResponse.ok) {
        const crawlData = await crawlResponse.json();
        combinedStats = { ...crawlData };
      }
      
      if (aiResponse.ok) {
        const aiData = await aiResponse.json();
        combinedStats = { 
          ...combinedStats,
          overall_stats: aiData.overall_stats,
          ai_knowledge_stats: aiData.ai_knowledge_stats 
        };
      }
      
      setStats(combinedStats);
    } catch (error) {
      console.error('통계 로딩 오류:', error);
    }
  };

  // AI 지식 생성 (단일)
  const handleAiGenerate = async () => {
    if (!aiTopic.trim()) {
      alert('주제를 입력해주세요.');
      return;
    }

    setAiLoading(true);
    setAiResult(null);

    try {
      const response = await fetch(`${API_BASE}/ai-knowledge/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          topic: aiTopic,
          num_articles: aiNumArticles.toString()
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setAiResult(data);
      } else {
        const error = await response.text();
        alert(`AI 지식 생성 실패: ${error}`);
      }
    } catch (error) {
      console.error('AI 지식 생성 오류:', error);
      alert('AI 지식 생성 중 오류가 발생했습니다.');
    } finally {
      setAiLoading(false);
    }
  };

  // AI 지식 배치 생성
  const handleAiBatchGenerate = async () => {
    const topics = aiTopics.trim().split('\n').filter(q => q.trim());
    
    if (topics.length === 0) {
      alert('최소 1개 이상의 주제를 입력해주세요.');
      return;
    }

    if (topics.length > 5) {
      alert('한 번에 최대 5개까지만 처리 가능합니다.');
      return;
    }

    setAiBatchLoading(true);
    setAiBatchResult(null);

    try {
      const response = await fetch(`${API_BASE}/ai-knowledge/batch-generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topics: topics,
          articles_per_topic: aiArticlesPerTopic
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setAiBatchResult(data);
      } else {
        const error = await response.text();
        alert(`AI 지식 배치 생성 실패: ${error}`);
      }
    } catch (error) {
      console.error('AI 지식 배치 생성 오류:', error);
      alert('AI 지식 배치 생성 중 오류가 발생했습니다.');
    } finally {
      setAiBatchLoading(false);
    }
  };

  // AI 지식 생성 기능 정보 로드
  const loadAiCapabilities = async () => {
    try {
      const response = await fetch(`${API_BASE}/ai-knowledge/capabilities`);
      if (response.ok) {
        const data = await response.json();
        setAiCapabilities(data);
      }
    } catch (error) {
      console.error('AI 기능 정보 로딩 오류:', error);
    }
  };

  // 컴포넌트 마운트 시 소스 및 통계 로드
  React.useEffect(() => {
    loadSources();
    loadStats();
    loadAiCapabilities();
  }, []);

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      <div className="flex items-center space-x-2 mb-6">
        <Bot className="w-8 h-8 text-blue-600" />
        <h1 className="text-3xl font-bold">AI 강화 웹 크롤링 관리</h1>
      </div>

      <Tabs defaultValue="single" className="space-y-4">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="single">단일 크롤링</TabsTrigger>
          <TabsTrigger value="batch">배치 크롤링</TabsTrigger>
          <TabsTrigger value="ai-generate">AI 지식 생성</TabsTrigger>
          <TabsTrigger value="sources">크롤링 소스</TabsTrigger>
          <TabsTrigger value="stats">통계</TabsTrigger>
        </TabsList>

        {/* 단일 크롤링 탭 */}
        <TabsContent value="single">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Search className="w-5 h-5" />
                <span>단일 주제 AI 크롤링</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium mb-2">검색어</label>
                  <Input
                    value={singleQuery}
                    onChange={(e) => setSingleQuery(e.target.value)}
                    placeholder="예: 인공지능, 기후변화, 한국사"
                    className="w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">수집 개수</label>
                  <Input
                    type="number"
                    value={numResults}
                    onChange={(e) => setNumResults(Number(e.target.value))}
                    min="5"
                    max="50"
                    className="w-full"
                  />
                </div>
              </div>

              <Button
                onClick={handleSingleCrawl}
                disabled={loading || !singleQuery.trim()}
                className="w-full md:w-auto"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    AI 크롤링 진행 중...
                  </>
                ) : (
                  <>
                    <Zap className="w-4 h-4 mr-2" />
                    AI 크롤링 시작
                  </>
                )}
              </Button>

              {singleResult && (
                <Alert className="mt-4">
                  <CheckCircle className="w-4 h-4" />
                  <AlertDescription>
                    <div className="space-y-2">
                      <p><strong>검색어:</strong> {singleResult.query}</p>
                      <p><strong>수집 결과:</strong> {singleResult.summary.total_collected}개 수집, {singleResult.summary.successfully_saved}개 저장</p>
                      <p><strong>성공률:</strong> {singleResult.summary.coverage_ratio}</p>
                      <p><strong>사용 소스:</strong> {singleResult.summary.sources_used.join(', ')}</p>
                      <p className="text-green-600">{singleResult.message}</p>
                    </div>
                  </AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* 배치 크롤링 탭 */}
        <TabsContent value="batch">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Database className="w-5 h-5" />
                <span>배치 AI 크롤링</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">
                    검색어 목록 (한 줄에 하나씩, 최대 10개)
                  </label>
                  <Textarea
                    value={batchQueries}
                    onChange={(e) => setBatchQueries(e.target.value)}
                    placeholder={`인공지능\n기후변화\n한국사\n경제학\n교육정책`}
                    rows={8}
                    className="w-full"
                  />
                </div>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">주제별 수집 개수</label>
                    <Input
                      type="number"
                      value={resultsPerQuery}
                      onChange={(e) => setResultsPerQuery(Number(e.target.value))}
                      min="5"
                      max="20"
                      className="w-full"
                    />
                  </div>
                  <Alert>
                    <AlertDescription>
                      여러 주제를 동시에 크롤링합니다. 각 주제마다 다양한 소스에서 콘텐츠를 수집합니다.
                    </AlertDescription>
                  </Alert>
                </div>
              </div>

              <Button
                onClick={handleBatchCrawl}
                disabled={batchLoading || !batchQueries.trim()}
                className="w-full md:w-auto"
              >
                {batchLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    배치 크롤링 진행 중...
                  </>
                ) : (
                  <>
                    <Database className="w-4 h-4 mr-2" />
                    배치 크롤링 시작
                  </>
                )}
              </Button>

              {batchResult && (
                <div className="mt-4 space-y-4">
                  <Alert>
                    <CheckCircle className="w-4 h-4" />
                    <AlertDescription>
                      <div className="space-y-2">
                        <p><strong>전체 요약:</strong></p>
                        <p>• 처리 주제: {batchResult.batch_summary.total_queries}개</p>
                        <p>• 성공: {batchResult.batch_summary.successful}개</p>
                        <p>• 실패: {batchResult.batch_summary.failed}개</p>
                        <p>• 총 수집: {batchResult.batch_summary.total_collected}개</p>
                        <p>• 총 저장: {batchResult.batch_summary.total_saved}개</p>
                        <p>• 성공률: {batchResult.batch_summary.success_rate}</p>
                      </div>
                    </AlertDescription>
                  </Alert>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {batchResult.results.map((result, index) => (
                      <Card key={index} className={result.status === 'success' ? 'border-green-200' : 'border-red-200'}>
                        <CardContent className="p-4">
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-medium">{result.query}</h4>
                            {result.status === 'success' ? (
                              <CheckCircle className="w-5 h-5 text-green-500" />
                            ) : (
                              <XCircle className="w-5 h-5 text-red-500" />
                            )}
                          </div>
                          {result.status === 'success' ? (
                            <div className="text-sm text-gray-600 space-y-1">
                              <p>수집: {result.collected}개</p>
                              <p>저장: {result.saved}개</p>
                              <p>소스: {result.sources?.join(', ') || '없음'}</p>
                            </div>
                          ) : (
                            <p className="text-sm text-red-600">{result.error}</p>
                          )}
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* AI 지식 생성 탭 */}
        <TabsContent value="ai-generate">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 단일 AI 지식 생성 */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Bot className="w-5 h-5" />
                  <span>단일 주제 AI 지식 생성</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">주제</label>
                  <Input
                    value={aiTopic}
                    onChange={(e) => setAiTopic(e.target.value)}
                    placeholder="예: 인공지능, 기후변화, 교육"
                    className="w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">생성할 문서 수</label>
                  <Input
                    type="number"
                    value={aiNumArticles}
                    onChange={(e) => setAiNumArticles(Number(e.target.value))}
                    min="1"
                    max="10"
                    className="w-full"
                  />
                </div>

                <Button
                  onClick={handleAiGenerate}
                  disabled={aiLoading || !aiTopic.trim()}
                  className="w-full"
                >
                  {aiLoading ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      AI 지식 생성 중...
                    </>
                  ) : (
                    <>
                      <Bot className="w-4 h-4 mr-2" />
                      Claude AI로 지식 생성
                    </>
                  )}
                </Button>

                {aiResult && (
                  <Alert className="mt-4">
                    <CheckCircle className="w-4 h-4" />
                    <AlertDescription>
                      <div className="space-y-2">
                        <p><strong>주제:</strong> {aiResult.topic}</p>
                        <p><strong>생성 결과:</strong> {aiResult.summary.generated_articles}개 생성, {aiResult.summary.saved_articles}개 저장</p>
                        <p><strong>생성률:</strong> {aiResult.summary.generation_rate}</p>
                        <p><strong>저장률:</strong> {aiResult.summary.save_rate}</p>
                        <p className="text-green-600">{aiResult.message}</p>
                      </div>
                    </AlertDescription>
                  </Alert>
                )}
              </CardContent>
            </Card>

            {/* AI 지식 배치 생성 */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Database className="w-5 h-5" />
                  <span>배치 AI 지식 생성</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">
                    주제 목록 (한 줄에 하나씩, 최대 5개)
                  </label>
                  <Textarea
                    value={aiTopics}
                    onChange={(e) => setAiTopics(e.target.value)}
                    placeholder={`인공지능\n기후변화\n디지털 교육\n경제학\n사회 문제`}
                    rows={6}
                    className="w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">주제별 문서 수</label>
                  <Input
                    type="number"
                    value={aiArticlesPerTopic}
                    onChange={(e) => setAiArticlesPerTopic(Number(e.target.value))}
                    min="1"
                    max="5"
                    className="w-full"
                  />
                </div>

                <Button
                  onClick={handleAiBatchGenerate}
                  disabled={aiBatchLoading || !aiTopics.trim()}
                  className="w-full"
                >
                  {aiBatchLoading ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      AI 배치 생성 중...
                    </>
                  ) : (
                    <>
                      <Database className="w-4 h-4 mr-2" />
                      AI 배치 지식 생성
                    </>
                  )}
                </Button>

                {aiBatchResult && (
                  <div className="mt-4 space-y-4">
                    <Alert>
                      <CheckCircle className="w-4 h-4" />
                      <AlertDescription>
                        <div className="space-y-2">
                          <p><strong>배치 생성 요약:</strong></p>
                          <p>• 처리 주제: {aiBatchResult.batch_summary.total_topics}개</p>
                          <p>• 성공: {aiBatchResult.batch_summary.successful}개</p>
                          <p>• 실패: {aiBatchResult.batch_summary.failed}개</p>
                          <p>• 총 생성: {aiBatchResult.batch_summary.total_generated}개</p>
                          <p>• 총 저장: {aiBatchResult.batch_summary.total_saved}개</p>
                          <p>• 성공률: {aiBatchResult.batch_summary.success_rate}</p>
                        </div>
                      </AlertDescription>
                    </Alert>

                    <div className="grid grid-cols-1 gap-3 max-h-60 overflow-y-auto">
                      {aiBatchResult.results.map((result: any, index: number) => (
                        <Card key={index} className={result.status === 'success' ? 'border-green-200' : 'border-red-200'}>
                          <CardContent className="p-3">
                            <div className="flex items-center justify-between mb-2">
                              <h4 className="font-medium text-sm">{result.topic}</h4>
                              {result.status === 'success' ? (
                                <CheckCircle className="w-4 h-4 text-green-500" />
                              ) : (
                                <XCircle className="w-4 h-4 text-red-500" />
                              )}
                            </div>
                            {result.status === 'success' ? (
                              <div className="text-xs text-gray-600 space-y-1">
                                <p>생성: {result.generated}개</p>
                                <p>저장: {result.saved}개</p>
                                {result.contents && result.contents.length > 0 && (
                                  <p>콘텐츠: {result.contents[0]?.title?.substring(0, 30)}...</p>
                                )}
                              </div>
                            ) : (
                              <p className="text-xs text-red-600">{result.error}</p>
                            )}
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* AI 기능 소개 */}
          {aiCapabilities && (
            <Card className="mt-6">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Zap className="w-5 h-5" />
                  <span>Claude AI 지식 생성기 특징</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div>
                    <h4 className="font-medium mb-3 text-blue-600">지원 주제</h4>
                    <div className="flex flex-wrap gap-2">
                      {aiCapabilities.ai_generator_info.supported_topics.map((topic: string, index: number) => (
                        <Badge key={index} variant="outline">{topic}</Badge>
                      ))}
                    </div>
                  </div>
                  <div>
                    <h4 className="font-medium mb-3 text-green-600">주요 기능</h4>
                    <ul className="text-sm space-y-1">
                      {aiCapabilities.ai_generator_info.features.slice(0, 4).map((feature: string, index: number) => (
                        <li key={index}>• {feature}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h4 className="font-medium mb-3 text-purple-600">장점</h4>
                    <ul className="text-sm space-y-1">
                      {aiCapabilities.ai_generator_info.advantages.slice(0, 4).map((advantage: string, index: number) => (
                        <li key={index}>• {advantage}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* 크롤링 소스 탭 */}
        <TabsContent value="sources">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Globe className="w-5 h-5" />
                <span>지원 크롤링 소스</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {sources.map((source, index) => (
                  <Card key={index} className="border-blue-200">
                    <CardContent className="p-4">
                      <h4 className="font-medium mb-2">{source.name}</h4>
                      <p className="text-sm text-gray-600 mb-2">{source.domain}</p>
                      <p className="text-sm">{source.description}</p>
                      <Badge variant="secondary" className="mt-2">
                        활성화
                      </Badge>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 통계 탭 */}
        <TabsContent value="stats">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <BarChart3 className="w-5 h-5" />
                <span>크롤링 통계</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {stats && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-medium mb-3">데이터베이스 통계</h4>
                    <div className="space-y-2 text-sm">
                      <p>• 총 문서: {stats.overall_stats?.total_documents || 0}개</p>
                      <p>• 활성 문서: {stats.overall_stats?.active_documents || 0}개</p>
                      <p>• 표절 검사: {stats.overall_stats?.total_checks || 0}건</p>
                      <p>• AI 생성 문서: {stats.ai_knowledge_stats?.total_ai_documents || 0}개</p>
                    </div>
                  </div>
                  <div>
                    <h4 className="font-medium mb-3">AI 시스템 통계</h4>
                    <div className="space-y-2 text-sm">
                      <p>• 크롤링 소스: {stats.ai_crawling_stats?.supported_sources || 0}개</p>
                      <p>• AI 문서 생성: {stats.ai_knowledge_stats?.ai_generation_enabled ? '활성화' : '비활성화'}</p>
                      <p>• 지원 언어: {stats.ai_knowledge_stats?.supported_languages?.join(', ') || '한국어'}</p>
                      <div className="mt-3">
                        <p className="font-medium mb-1">AI 생성 기능:</p>
                        <ul className="list-disc list-inside space-y-1">
                          {stats.ai_knowledge_stats?.generation_capabilities?.map((capability: string, index: number) => (
                            <li key={index}>{capability}</li>
                          )) || []}
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AICrawlingManager;