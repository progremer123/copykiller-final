import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { CheckCircle, AlertTriangle, XCircle, Download, ExternalLink, Clock } from 'lucide-react';
import { CheckResult } from './PlagiarismChecker';
import { cn } from '@/lib/utils';

interface ResultsDisplayProps {
  results: CheckResult[];
}

export const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ results }) => {
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

  const highlightText = (text: string, matches: CheckResult['matches']) => {
    if (!matches.length) return text;

    let highlightedText = text;
    const sortedMatches = [...matches].sort((a, b) => b.startIndex - a.startIndex);

    sortedMatches.forEach((match) => {
      const beforeText = highlightedText.substring(0, match.startIndex);
      const matchText = highlightedText.substring(match.startIndex, match.endIndex);
      const afterText = highlightedText.substring(match.endIndex);

      const colorClass = match.similarity > 80 ? 'highlight-high' : 
                        match.similarity > 60 ? 'highlight-medium' : 'highlight-low';

      highlightedText = (
        beforeText +
        `<mark class="bg-${colorClass} px-1 py-0.5 rounded font-medium" title="${match.source} (${match.similarity}% 유사)">${matchText}</mark>` +
        afterText
      );
    });

    return highlightedText;
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
                  <h4 className="font-semibold">분석된 텍스트</h4>
                  <Card>
                    <CardContent className="p-4">
                      <div 
                        className="prose max-w-none leading-relaxed"
                        dangerouslySetInnerHTML={{
                          __html: highlightText(result.originalText, result.matches)
                        }}
                      />
                    </CardContent>
                  </Card>
                </div>

                {/* Matches */}
                {result.matches.length > 0 && (
                  <div className="space-y-3">
                    <h4 className="font-semibold">발견된 일치 항목</h4>
                    <div className="space-y-3">
                      {result.matches.map((match, index) => (
                        <Card key={index}>
                          <CardContent className="p-4">
                            <div className="flex items-start justify-between mb-2">
                              <div className="space-y-1">
                                <p className="font-medium text-sm">{match.source}</p>
                                <Badge variant="outline">
                                  {match.similarity}% 유사
                                </Badge>
                              </div>
                              <Button variant="ghost" size="sm">
                                <ExternalLink className="h-4 w-4" />
                              </Button>
                            </div>
                            <p className="text-sm bg-muted p-3 rounded italic">
                              "{match.text}"
                            </p>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </div>
                )}

                {/* Actions */}
                <div className="flex space-x-2 pt-4 border-t">
                  <Button variant="outline" size="sm">
                    <Download className="h-4 w-4 mr-2" />
                    리포트 다운로드
                  </Button>
                  <Button variant="outline" size="sm">
                    <ExternalLink className="h-4 w-4 mr-2" />
                    상세 분석
                  </Button>
                </div>
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