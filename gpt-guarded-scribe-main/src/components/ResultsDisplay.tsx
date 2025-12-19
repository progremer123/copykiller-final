import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { CheckCircle, AlertTriangle, XCircle, Download, ExternalLink, Clock, Lightbulb, Shield } from 'lucide-react';
import { CheckResult } from './PlagiarismChecker';
import { cn } from '@/lib/utils';
import { AdvancedAnalysis } from './AdvancedAnalysis';
import { SentenceImprovement } from './SentenceImprovement';
import AIPlagiarismAvoidance from './AIPlagiarismAvoidance';

interface ResultsDisplayProps {
  results: CheckResult[];
  onSelectResult?: (result: CheckResult) => void;
}

export const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ results, onSelectResult }) => {
  const [showImprovement, setShowImprovement] = React.useState<string | null>(null);
  const [showAvoidance, setShowAvoidance] = React.useState<string | null>(null);
  const getSimilarityColor = (similarity: number) => {
    if (similarity < 15) return 'success';
    if (similarity < 40) return 'warning';
    return 'destructive';
  };

  const getSimilarityIcon = (similarity: number) => {
    if (similarity < 15) return <CheckCircle className="h-5 w-5" />;
    if (similarity < 40) return <AlertTriangle className="h-5 w-5" />;
    return <XCircle className="h-5 w-5" />;
  };

  const getSimilarityLabel = (similarity: number) => {
    if (similarity < 15) return '안전';
    if (similarity < 40) return '주의';
    return '위험';
  };

  const highlightText = (text: string, matches: Array<{startIndex: number, endIndex: number}>) => {
    if (!matches || matches.length === 0) return text;
    
    // 매치를 시작 위치 기준으로 정렬하고 중복 제거
    const sortedMatches = matches
      .filter(match => match.startIndex >= 0 && match.endIndex <= text.length && match.startIndex < match.endIndex)
      .sort((a, b) => a.startIndex - b.startIndex);
    
    // 겹치는 매치 병합
    const mergedMatches = [];
    for (const match of sortedMatches) {
      if (mergedMatches.length === 0) {
        mergedMatches.push({ start: match.startIndex, end: match.endIndex });
      } else {
        const last = mergedMatches[mergedMatches.length - 1];
        if (match.startIndex <= last.end) {
          // 겹치는 경우 병합
          last.end = Math.max(last.end, match.endIndex);
        } else {
          mergedMatches.push({ start: match.startIndex, end: match.endIndex });
        }
      }
    }
    
    const result = [];
    let lastEnd = 0;
    
    mergedMatches.forEach((segment, index) => {
      // 이전 세그먼트 이후부터 현재 세그먼트 이전까지의 텍스트
      if (segment.start > lastEnd) {
        result.push(text.slice(lastEnd, segment.start));
      }
      
      // 현재 세그먼트 (하이라이트) - 개선된 스타일링
      const highlightedText = text.slice(segment.start, segment.end);
      if (highlightedText.trim().length > 0) {
        result.push(
          <mark 
            key={index} 
            className="bg-yellow-200 border border-orange-400 px-2 py-1 rounded-md font-semibold text-orange-900 shadow-sm"
            title={`표절 의심 구간 (${index + 1})`}
            style={{
              background: 'linear-gradient(135deg, #fef3c7 0%, #fed7aa 100%)',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
            }}
          >
            {highlightedText}
          </mark>
        );
      }
      
      lastEnd = segment.end;
    });
    
    // 마지막 세그먼트 이후의 텍스트
    if (lastEnd < text.length) {
      result.push(text.slice(lastEnd));
    }
    
    return result;
  };

  if (results.length === 0) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <div className="space-y-4">
            <div className="w-16 h-16 mx-auto bg-muted rounded-full flex items-center justify-center">
              <Clock className="h-8 w-8 text-muted-foreground" />
            </div>
            <h3 className="text-lg font-medium">아직 검사 결과가 없습니다</h3>
            <p className="text-muted-foreground">
              파일을 업로드하거나 텍스트를 입력하여 표절 검사를 시작하세요.
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {results.map((result) => (
        <Card key={result.id} className="overflow-hidden">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg">
                검사 결과 #{result.id}
              </CardTitle>
              <div className="flex items-center space-x-2">
                <Badge variant="secondary">
                  {result.timestamp.toLocaleDateString()} {result.timestamp.toLocaleTimeString()}
                </Badge>
              </div>
            </div>
          </CardHeader>

          <CardContent className="space-y-6">
            {result.status === 'checking' && (
              <div className="space-y-4">
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>
                  <span className="text-sm text-muted-foreground">표절 검사 진행 중...</span>
                </div>
                <Progress value={66} className="w-full" />
              </div>
            )}

            {result.status === 'completed' && (
              <>
                {/* Similarity Score */}
                <div className="flex items-center justify-between p-4 rounded-lg border">
                  <div className="flex items-center space-x-3">
                    <div className={cn(
                      "flex items-center justify-center w-10 h-10 rounded-full",
                      getSimilarityColor(result.similarity) === 'success' ? 'bg-success text-success-foreground' :
                      getSimilarityColor(result.similarity) === 'warning' ? 'bg-warning text-warning-foreground' :
                      'bg-destructive text-destructive-foreground'
                    )}>
                      {getSimilarityIcon(result.similarity)}
                    </div>
                    <div>
                      <h3 className="font-semibold">유사도 점수</h3>
                      <p className="text-sm text-muted-foreground">
                        {getSimilarityLabel(result.similarity)} - {result.matches.length}개 일치 발견
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-3xl font-bold">
                      {result.similarity.toFixed(1)}%
                    </div>
                    <Badge variant={
                      getSimilarityColor(result.similarity) === 'success' ? 'default' :
                      getSimilarityColor(result.similarity) === 'warning' ? 'secondary' : 'destructive'
                    }>
                      {getSimilarityLabel(result.similarity)}
                    </Badge>
                  </div>
                </div>

                {/* Highlighted Text */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <h4 className="font-semibold">분석된 텍스트</h4>
                    {result.matches.length > 0 && (
                      <Badge variant="outline" className="text-xs">
                        🎯 {result.matches.length}개 구간 매칭됨
                      </Badge>
                    )}
                  </div>
                  <Card className="border-2">
                    <CardContent className="p-4">
                      <div className="prose max-w-none leading-relaxed text-sm">
                        {highlightText(result.originalText, result.matches)}
                      </div>
                      {result.matches.length > 0 && (
                        <div className="mt-4 pt-3 border-t border-gray-200">
                          <p className="text-xs text-gray-500 flex items-center gap-1">
                            <span className="inline-block w-3 h-3 rounded" 
                                  style={{ background: 'linear-gradient(135deg, #fef3c7 0%, #fed7aa 100%)' }}></span>
                            하이라이트된 구간: 표절 의심 부분
                          </p>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </div>

                {/* Matches */}
                {result.matches.length > 0 && (
                  <div className="space-y-3">
                    <h4 className="font-semibold">발견된 일치 항목</h4>
                    <div className="space-y-3">
                      {result.matches.map((match, index) => (
                        <Card key={index} className="border-l-4 border-l-orange-400">
                          <CardContent className="p-4">
                            <div className="flex items-start justify-between mb-3">
                              <div className="space-y-2">
                                <div className="flex items-center gap-2">
                                  <p className="font-medium text-sm">{match.source}</p>
                                  {(match as any).match_type && (
                                    <Badge variant="secondary" className="text-xs">
                                      {(match as any).match_type === 'sentence' ? '📝 문장' :
                                       (match as any).match_type === 'phrase' ? '📄 구문' :
                                       (match as any).match_type === 'keyword' ? '🔑 키워드' : '📊 일반'}
                                    </Badge>
                                  )}
                                </div>
                                <div className="flex items-center gap-2">
                                  <Badge 
                                    variant={match.similarity >= 70 ? "destructive" : 
                                             match.similarity >= 40 ? "default" : "secondary"}
                                  >
                                    {match.similarity.toFixed(1)}% 유사
                                  </Badge>
                                  <span className="text-xs text-gray-500">
                                    위치: {match.startIndex}-{match.endIndex}
                                  </span>
                                </div>
                              </div>
                              <Button variant="ghost" size="sm">
                                <ExternalLink className="h-4 w-4" />
                              </Button>
                            </div>
                            <div className="bg-orange-50 border border-orange-200 p-3 rounded-lg">
                              <p className="text-sm text-orange-900 font-medium">
                                📋 매칭된 내용:
                              </p>
                              <p className="text-sm text-gray-700 mt-1 italic">
                                "{match.text}"
                              </p>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </div>
                )}

                {/* Actions */}
                <div className="flex flex-wrap gap-2 pt-4 border-t">
                  <Button 
                    variant="default" 
                    size="sm"
                    onClick={() => onSelectResult?.(result)}
                  >
                    <ExternalLink className="h-4 w-4 mr-2" />
                    AI 고급 분석 실행
                  </Button>
                  <Button 
                    variant="secondary" 
                    size="sm"
                    onClick={() => setShowImprovement(showImprovement === result.id ? null : result.id)}
                  >
                    <Lightbulb className="h-4 w-4 mr-2" />
                    문장 개선 제안
                  </Button>
                  {result.similarity >= 15 && (
                    <Button 
                      variant="destructive" 
                      size="sm"
                      onClick={() => setShowAvoidance(showAvoidance === result.id ? null : result.id)}
                    >
                      <Shield className="h-4 w-4 mr-2" />
                      AI 표절 회피
                    </Button>
                  )}
                  <Button variant="outline" size="sm">
                    <Download className="h-4 w-4 mr-2" />
                    리포트 다운로드
                  </Button>
                </div>

                {/* 문장 개선 제안 */}
                {showImprovement === result.id && (
                  <div className="mt-6">
                    <SentenceImprovement 
                      checkResult={result}
                      onClose={() => setShowImprovement(null)}
                    />
                  </div>
                )}

                {/* AI 표절 회피 */}
                {showAvoidance === result.id && (
                  <div className="mt-6">
                    <Card className="border-red-200 bg-red-50">
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2 text-red-700">
                          <Shield className="h-5 w-5" />
                          AI 표절 회피 시스템
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <AIPlagiarismAvoidance 
                          checkId={result.id}
                          initialText={result.originalText}
                          onAvoidanceComplete={() => setShowAvoidance(null)}
                        />
                      </CardContent>
                    </Card>
                  </div>
                )}
              </>
            )}

            {result.status === 'error' && (
              <div className="text-center py-8">
                <XCircle className="h-12 w-12 text-destructive mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">검사 중 오류가 발생했습니다</h3>
                <p className="text-muted-foreground">잠시 후 다시 시도해주세요.</p>
              </div>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  );
};