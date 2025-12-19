import React, { useState } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';
import { Progress } from './ui/progress';
import { Alert, AlertDescription } from './ui/alert';
import { 
  Bot, 
  RefreshCw, 
  CheckCircle, 
  ArrowRight,
  TrendingDown,
  Lightbulb,
  FileText,
  Zap
} from 'lucide-react';

interface PlagiarismMatch {
  start_index: number;
  end_index: number;
  similarity_score: number;
  matched_text: string;
  source_title: string;
}

interface FixedSection {
  section_number: number;
  original_text: string;
  fixed_text: string;
  similarity_before: number;
  similarity_after: number;
  techniques_used: string[];
  improvement: number;
}

interface AIPlagiarismFixerProps {
  originalText: string;
  plagiarismMatches: PlagiarismMatch[];
  checkId?: string;
  onFixApplied?: (fixedText: string) => void;
}

const AIPlagiarismFixer: React.FC<AIPlagiarismFixerProps> = ({
  originalText,
  plagiarismMatches,
  checkId,
  onFixApplied
}) => {
  const [isFixing, setIsFixing] = useState(false);
  const [fixResult, setFixResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  // 90% 이상 고유사도 매치 필터링
  const highSimilarityMatches = plagiarismMatches.filter(match => 
    match.similarity_score >= 0.90
  );

  const handleAIFix = async () => {
    if (!originalText || originalText.length < 10) {
      setError('텍스트가 너무 짧습니다 (최소 10자 이상)');
      return;
    }

    setIsFixing(true);
    setError(null);
    setFixResult(null);

    try {
      const response = await fetch('/api/ai-fix/plagiarism', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: originalText,
          plagiarism_matches: highSimilarityMatches
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      setFixResult(result);

      if (result.success && result.fixed_text && onFixApplied) {
        onFixApplied(result.fixed_text);
      }

    } catch (err) {
      console.error('AI 표절 회피 오류:', err);
      setError(err instanceof Error ? err.message : 'AI 표절 회피 중 오류가 발생했습니다');
    } finally {
      setIsFixing(false);
    }
  };

  const handleFixByCheckId = async () => {
    if (!checkId) {
      setError('검사 ID가 없습니다');
      return;
    }

    setIsFixing(true);
    setError(null);
    setFixResult(null);

    try {
      const response = await fetch(`/api/plagiarism/ai-fix/check/${checkId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      setFixResult(result);

      if (result.success && result.fixed_text && onFixApplied) {
        onFixApplied(result.fixed_text);
      }

    } catch (err) {
      console.error('검사 ID 기반 표절 회피 오류:', err);
      setError(err instanceof Error ? err.message : 'AI 표절 회피 중 오류가 발생했습니다');
    } finally {
      setIsFixing(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* AI 표절 회피 시스템 소개 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bot className="h-5 w-5 text-blue-600" />
            AI 자동 표절 회피 시스템
          </CardTitle>
          <CardDescription>
            유사도가 90% 이상인 고위험 구간을 AI가 자동으로 감지하여 표절을 회피하도록 수정합니다
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {highSimilarityMatches.length}
              </div>
              <div className="text-sm text-gray-600">고위험 구간</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">4</div>
              <div className="text-sm text-gray-600">AI 기법</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">90%+</div>
              <div className="text-sm text-gray-600">수정 대상</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">
                <Zap className="h-6 w-6 mx-auto" />
              </div>
              <div className="text-sm text-gray-600">실시간</div>
            </div>
          </div>

          <div className="flex flex-wrap gap-2 mb-4">
            <Badge variant="outline">동의어 교체</Badge>
            <Badge variant="outline">문장 구조 변경</Badge>
            <Badge variant="outline">표현 방식 전환</Badge>
            <Badge variant="outline">문장 순서 조정</Badge>
          </div>

          <div className="flex gap-2">
            <Button 
              onClick={handleAIFix}
              disabled={isFixing || highSimilarityMatches.length === 0}
              className="flex-1"
            >
              {isFixing ? (
                <>
                  <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                  AI 수정 중...
                </>
              ) : (
                <>
                  <Bot className="mr-2 h-4 w-4" />
                  AI 자동 수정 시작
                </>
              )}
            </Button>

            {checkId && (
              <Button 
                onClick={handleFixByCheckId}
                disabled={isFixing}
                variant="outline"
              >
                검사 결과로 수정
              </Button>
            )}
          </div>

          {highSimilarityMatches.length === 0 && (
            <Alert className="mt-4">
              <CheckCircle className="h-4 w-4" />
              <AlertDescription>
                90% 이상 고유사도 구간이 없어 자동 수정이 필요하지 않습니다.
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* 오류 표시 */}
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* AI 수정 결과 */}
      {fixResult && (
        <div className="space-y-4">
          {/* 수정 요약 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-green-600" />
                AI 수정 완료
              </CardTitle>
              <CardDescription>{fixResult.message}</CardDescription>
            </CardHeader>
            <CardContent>
              {fixResult.summary && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                  <div className="text-center p-3 bg-blue-50 rounded-lg">
                    <div className="text-xl font-bold text-blue-600">
                      {fixResult.summary.total_fixes}
                    </div>
                    <div className="text-sm text-blue-800">수정된 구간</div>
                  </div>
                  <div className="text-center p-3 bg-green-50 rounded-lg">
                    <div className="text-xl font-bold text-green-600">
                      {fixResult.summary.average_similarity_reduction}
                    </div>
                    <div className="text-sm text-green-800">평균 유사도 감소</div>
                  </div>
                  <div className="text-center p-3 bg-purple-50 rounded-lg">
                    <div className="text-xl font-bold text-purple-600">
                      {fixResult.summary.total_similarity_improvement}
                    </div>
                    <div className="text-sm text-purple-800">전체 개선도</div>
                  </div>
                </div>
              )}

              {fixResult.ai_techniques_used && (
                <div className="mb-4">
                  <div className="text-sm font-medium mb-2">적용된 AI 기법:</div>
                  <div className="flex flex-wrap gap-2">
                    {fixResult.ai_techniques_used.map((technique: string, index: number) => (
                      <Badge key={index} variant="secondary">
                        {technique}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* 수정된 구간 상세 */}
          {fixResult.fixes_applied && fixResult.fixes_applied.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5 text-blue-600" />
                  수정 상세 내역
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {fixResult.fixes_applied.map((fix: FixedSection, index: number) => (
                    <div key={index} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <h4 className="font-medium">구간 {fix.section_number}</h4>
                        <div className="flex items-center gap-2">
                          <Badge variant="destructive">
                            {(fix.similarity_before * 100).toFixed(1)}%
                          </Badge>
                          <ArrowRight className="h-4 w-4 text-gray-400" />
                          <Badge variant="secondary">
                            {(fix.similarity_after * 100).toFixed(1)}%
                          </Badge>
                          <TrendingDown className="h-4 w-4 text-green-600" />
                          <span className="text-green-600 font-medium">
                            -{(fix.improvement * 100).toFixed(1)}%
                          </span>
                        </div>
                      </div>

                      <div className="space-y-3">
                        <div>
                          <div className="text-sm font-medium text-gray-700 mb-1">원본:</div>
                          <div className="text-sm bg-red-50 p-2 rounded border-l-4 border-red-500">
                            {fix.original_text}
                          </div>
                        </div>

                        <div>
                          <div className="text-sm font-medium text-gray-700 mb-1">수정됨:</div>
                          <div className="text-sm bg-green-50 p-2 rounded border-l-4 border-green-500">
                            {fix.fixed_text}
                          </div>
                        </div>

                        <div>
                          <div className="text-sm font-medium text-gray-700 mb-1">적용 기법:</div>
                          <div className="flex flex-wrap gap-1">
                            {fix.techniques_used.map((technique: string, techIndex: number) => (
                              <Badge key={techIndex} variant="outline" className="text-xs">
                                {technique}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* AI 추천 사항 */}
          {fixResult.ai_recommendations && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Lightbulb className="h-5 w-5 text-yellow-600" />
                  AI 추천 사항
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {fixResult.ai_recommendations.map((recommendation: string, index: number) => (
                    <li key={index} className="flex items-start gap-2">
                      <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                      <span className="text-sm">{recommendation}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}

          {/* 수정된 텍스트 미리보기 */}
          {fixResult.fixed_text && fixResult.fixed_text !== fixResult.original_text && (
            <Card>
              <CardHeader>
                <CardTitle>수정된 텍스트 전체</CardTitle>
                <CardDescription>
                  AI가 수정한 전체 텍스트입니다. 복사하여 사용하세요.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="bg-gray-50 p-4 rounded-lg border">
                  <pre className="whitespace-pre-wrap text-sm font-mono">
                    {fixResult.fixed_text}
                  </pre>
                </div>
                <Button 
                  className="mt-3"
                  onClick={() => {
                    navigator.clipboard.writeText(fixResult.fixed_text);
                    // 토스트 메시지 표시 (선택적)
                  }}
                >
                  수정된 텍스트 복사
                </Button>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  );
};

export default AIPlagiarismFixer;