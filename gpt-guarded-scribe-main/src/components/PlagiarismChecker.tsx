import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Crown, Sparkles, User, LogOut, Bot, Shield } from 'lucide-react';
import { FileUpload } from './FileUpload';
import { TextInput } from './TextInput';
import { ResultsDisplay } from './ResultsDisplay';
import { SearchHistory } from './SearchHistory';
import { AdvancedAnalysis } from './AdvancedAnalysis';
import { PremiumFeatures } from './PremiumFeatures';
import AIPlagiarismFixer from './AIPlagiarismFixer';

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
  const [selectedResult, setSelectedResult] = useState<CheckResult | null>(null);
  const [isPremiumUser, setIsPremiumUser] = useState(false);
  const [dbStats, setDbStats] = useState<any>(null);
  const [user, setUser] = useState<any>(null);

  // 데이터베이스 상태 확인
  const fetchDbStats = async () => {
    try {
      const response = await axios.get('http://localhost:8006/api/database/stats');
      setDbStats(response.data);
    } catch (error) {
      console.error('DB 상태 확인 오류:', error);
    }
  };

  // 로그인 상태 확인
  const checkLoginStatus = () => {
    const token = localStorage.getItem('access_token');
    const userInfo = localStorage.getItem('user_info');
    
    if (token && userInfo) {
      try {
        const parsedUser = JSON.parse(userInfo);
        setUser(parsedUser);
        setIsPremiumUser(parsedUser.is_premium || false);
      } catch (error) {
        console.error('User info parsing error:', error);
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_info');
      }
    }
  };

  // 로그아웃 처리
  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_info');
    setUser(null);
    setIsPremiumUser(false);
  };

  // 표절 검사 시 로그인 사용자라면 질문 저장
  const saveUserQuestion = async (questionText: string, result: any) => {
    const token = localStorage.getItem('access_token');
    if (!token || !user) return;

    try {
      await axios.post('http://localhost:8006/api/auth/questions', {
        question_text: questionText,
        question_type: 'plagiarism_check',
        original_text: questionText.substring(0, 1000), // 처음 1000자만 저장
        similarity_score: result.similarity,
        match_count: result.matches?.length || 0,
        processing_time: result.processing_time
      }, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
    } catch (error) {
      console.error('Error saving user question:', error);
    }
  };

  // 컴포넌트 마운트 시 DB 상태 및 로그인 상태 확인
  React.useEffect(() => {
    fetchDbStats();
    checkLoginStatus();
  }, []);

  const handleTextSubmit = async (text: string) => {
    const newCheck: CheckResult = {
      id: Date.now().toString(), // 임시 ID로 우선 생성
      originalText: text,
      similarity: 0,
      matches: [],
      status: 'checking',
      timestamp: new Date()
    };
    setResults(prev => [newCheck, ...prev]);
    setActiveTab('results');

    try {
      console.log('🚀 API 요청 시작:', { text: text.substring(0, 50) + '...' });
      const response = await axios.post(
        'http://localhost:8006/api/check/text',
        { text },
        { 
          headers: { 'Content-Type': 'application/json' },
          timeout: 30000 // 30초 타임아웃
        }
      );
      console.log('✅ API 응답 받음:', response.data);

      const actualResult = response.data;

      const updatedResult = {
        ...newCheck,
        id: actualResult.id,
        status: actualResult.status,
        similarity: actualResult.similarity_score, 
        matches: actualResult.matches.map((match: any) => ({
          text: match.matched_text, 
          source: match.source_title,
          similarity: match.similarity_score,
          startIndex: match.start_index,
          endIndex: match.end_index
        })),
      };

      setResults(prev => prev.map(result =>
        result.id === newCheck.id ? updatedResult : result
      ));

      // 로그인 사용자라면 질문 기록 저장
      await saveUserQuestion(text, {
        similarity: actualResult.similarity_score,
        matches: actualResult.matches,
        processing_time: actualResult.processing_time
      });
    } catch (error) {
      console.error("텍스트 검사 API 오류:", error);
      if (axios.isAxiosError(error)) {
        console.error("응답 데이터:", error.response?.data);
        console.error("응답 상태:", error.response?.status);
        console.error("요청 설정:", error.config);
      }
      setResults(prev => prev.map(result => 
        result.id === newCheck.id ? { 
          ...result, 
          status: 'error',
          originalText: `오류: ${error instanceof Error ? error.message : '알 수 없는 오류'}`
        } : result
      ));
    }
  };

  // 파일 업로드 핸들러도 실제 API를 호출하도록 수정합니다.
  const handleFileSubmit = async (file: File) => {
    const newCheck: CheckResult = {
      id: Date.now().toString(),
      originalText: `Uploading file: ${file.name}`,
      similarity: 0,
      matches: [],
      status: 'checking',
      timestamp: new Date()
    };
    setResults(prev => [newCheck, ...prev]);
    setActiveTab('results');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('/api/check/file', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      const actualResult = response.data;
      
      const updatedFileResult = {
        ...newCheck,
        id: actualResult.id,
        originalText: actualResult.original_text,
        status: actualResult.status,
        similarity: actualResult.similarity_score,
        matches: actualResult.matches.map((match: any) => ({
            text: match.matched_text,
            source: match.source_title,
            similarity: match.similarity_score,
            startIndex: match.start_index,
            endIndex: match.end_index
        })),
      };

      setResults(prev => prev.map(result => 
        result.id === newCheck.id ? updatedFileResult : result
      ));

      // 로그인 사용자라면 질문 기록 저장
      await saveUserQuestion(`파일 업로드: ${file.name}`, {
        similarity: actualResult.similarity_score,
        matches: actualResult.matches,
        processing_time: actualResult.processing_time
      });
    } catch (error) {
      console.error("파일 업로드 API 오류:", error);
      if (axios.isAxiosError(error)) {
        console.error("응답 데이터:", error.response?.data);
        console.error("응답 상태:", error.response?.status);
      }
      setResults(prev => prev.map(result => 
        result.id === newCheck.id ? { 
          ...result, 
          status: 'error',
          originalText: `파일 업로드 오류: ${error instanceof Error ? error.message : '알 수 없는 오류'}`
        } : result
      ));
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <div className="text-center mb-8 bg-gradient-to-r from-blue-50 to-purple-50 p-8 rounded-lg relative">
          <div className="absolute top-4 right-4 flex gap-2">
            <Button asChild variant="outline" size="sm">
              <Link to="/ai-crawling" className="flex items-center gap-2">
                <Bot className="h-4 w-4" />
                AI 크롤링
              </Link>
            </Button>
            <Button asChild variant="destructive" size="sm">
              <Link to="/ai-plagiarism-avoidance" className="flex items-center gap-2">
                <Shield className="h-4 w-4" />
                AI 표절 회피
              </Link>
            </Button>
            <Button asChild variant="outline" size="sm">
              <Link to="/premium" className="flex items-center gap-2">
                <Crown className="h-4 w-4" />
                프리미엄
              </Link>
            </Button>
            {user ? (
              <>
                <Button asChild variant="outline" size="sm">
                  <Link to="/mypage" className="flex items-center gap-2">
                    <User className="h-4 w-4" />
                    {user.username}
                    {user.is_premium && <Crown className="h-3 w-3 text-yellow-500" />}
                  </Link>
                </Button>
                <Button variant="outline" size="sm" onClick={handleLogout}>
                  <LogOut className="h-4 w-4" />
                </Button>
              </>
            ) : (
              <Button asChild variant="outline" size="sm">
                <Link to="/login">로그인</Link>
              </Button>
            )}
          </div>
          <h1 className="text-4xl font-bold text-foreground mb-4 flex items-center justify-center gap-3">
            <Sparkles className="h-10 w-10 text-blue-600" />
            CopyKiller AI
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto mb-4">
            차세대 AI 기반 표절 검사로 학술 논문, 보고서, 에세이의 독창성을 확인하세요.
          </p>
          <div className="flex justify-center gap-2 mb-4 flex-wrap">
            <Badge className="bg-blue-100 text-blue-700">🤖 AI 분석</Badge>
            <Badge className="bg-purple-100 text-purple-700">💡 실시간 개선</Badge>
            <Badge className="bg-green-100 text-green-700">🎯 맥락 이해</Badge>
            {dbStats && (
              <Badge 
                className={`${
                  dbStats.status === 'healthy' 
                    ? 'bg-green-100 text-green-700' 
                    : 'bg-orange-100 text-orange-700'
                }`}
              >
                📚 데이터베이스: {dbStats.total_documents}개 문서
              </Badge>
            )}
          </div>
          <p className="text-sm text-gray-600">
            단순한 비교를 넘어 AI가 제공하는 스마트한 분석과 개선 제안
          </p>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-4 mb-8">
            <TabsTrigger value="upload">파일 업로드</TabsTrigger>
            <TabsTrigger value="text">텍스트 입력</TabsTrigger>
            <TabsTrigger value="results">결과 ({results.length})</TabsTrigger>
            <TabsTrigger value="premium" className="flex items-center gap-2">
              <Crown className="h-4 w-4" />
              프리미엄 기능
            </TabsTrigger>
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
              <CardContent className="space-y-4">
                <TextInput onTextSubmit={handleTextSubmit} />
                
                {/* API 테스트 버튼 */}
                <div className="border-t pt-4">
                  <p className="text-sm text-gray-600 mb-2">빠른 테스트:</p>
                  <Button 
                    onClick={() => handleTextSubmit("인공지능은 현대 기술의 핵심입니다. 머신러닝과 딥러닝을 통해 컴퓨터가 학습하고 판단할 수 있게 됩니다.")}
                    variant="outline"
                    size="sm"
                  >
                    샘플 텍스트로 테스트
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="results" className="space-y-6">
            <ResultsDisplay results={results} onSelectResult={setSelectedResult} />
            
            {selectedResult && selectedResult.status === 'completed' && (
              <>
                <AdvancedAnalysis 
                  text={selectedResult.originalText} 
                  matches={selectedResult.matches} 
                />
                
                {/* AI 표절 회피 시스템 */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Bot className="h-5 w-5 text-blue-600" />
                      AI 자동 표절 회피
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <AIPlagiarismFixer
                      originalText={selectedResult.originalText}
                      plagiarismMatches={selectedResult.matches.map(match => ({
                        start_index: match.startIndex,
                        end_index: match.endIndex,
                        similarity_score: match.similarity,
                        matched_text: match.text,
                        source_title: match.source
                      }))}
                      checkId={selectedResult.id}
                      onFixApplied={(fixedText) => {
                        // 수정된 텍스트로 새로운 검사 결과 생성 (선택적)
                        console.log('AI 수정된 텍스트:', fixedText);
                      }}
                    />
                  </CardContent>
                </Card>
              </>
            )}
            
            <SearchHistory results={results.filter(r => r.status === 'completed')} />
          </TabsContent>

          <TabsContent value="premium" className="space-y-6">
            <PremiumFeatures />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default PlagiarismChecker;