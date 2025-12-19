import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Lightbulb, 
  Copy, 
  CheckCircle, 
  TrendingUp, 
  BookOpen, 
  RefreshCw,
  Sparkles,
  ArrowRight,
  Info
} from 'lucide-react';
import { CheckResult } from './PlagiarismChecker';
import { cn } from '@/lib/utils';

interface ImprovementSuggestion {
  original_text: string;
  improved_text: string;
  type: string;
  confidence: number;
  explanation: string;
  position: {
    start: number;
    end: number;
  };
}

interface ImprovementData {
  total_suggestions: number;
  improvement_categories: Record<string, number>;
  suggestions: ImprovementSuggestion[];
}

interface SentenceImprovementProps {
  checkResult: CheckResult;
  onClose?: () => void;
}

export const SentenceImprovement: React.FC<SentenceImprovementProps> = ({ 
  checkResult, 
  onClose 
}) => {
  const [loading, setLoading] = useState(false);
  const [improvementData, setImprovementData] = useState<ImprovementData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  const fetchImprovements = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`http://localhost:8006/api/improve/check/${checkResult.id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success) {
        setImprovementData(data.improvement_data);
      } else {
        throw new Error(data.message || '개선 제안을 가져올 수 없습니다');
      }
    } catch (error) {
      console.error('개선 제안 API 오류:', error);
      setError(error instanceof Error ? error.message : '알 수 없는 오류가 발생했습니다');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = async (text: string, index: number) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 2000);
    } catch (error) {
      console.error('복사 실패:', error);
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case '표절 구간 패러프레이징':
        return <RefreshCw className="h-4 w-4" />;
      case '동의어 교체':
        return <BookOpen className="h-4 w-4" />;
      case '수동태 → 능동태':
        return <TrendingUp className="h-4 w-4" />;
      case '연결어 다양화':
        return <ArrowRight className="h-4 w-4" />;
      case '학술적 표현 개선':
        return <Sparkles className="h-4 w-4" />;
      case '문장 구조 개선':
        return <RefreshCw className="h-4 w-4" />;
      default:
        return <Lightbulb className="h-4 w-4" />;
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case '표절 구간 패러프레이징':
        return 'bg-red-100 text-red-800 border-red-200';
      case '동의어 교체':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case '수동태 → 능동태':
        return 'bg-green-100 text-green-800 border-green-200';
      case '연결어 다양화':
        return 'bg-purple-100 text-purple-800 border-purple-200';
      case '학술적 표현 개선':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case '문장 구조 개선':
        return 'bg-indigo-100 text-indigo-800 border-indigo-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 90) return 'text-green-600';
    if (confidence >= 75) return 'text-blue-600';
    if (confidence >= 60) return 'text-yellow-600';
    return 'text-gray-600';
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Lightbulb className="h-5 w-5 text-yellow-500" />
          AI 문장 개선 제안
        </CardTitle>
        <p className="text-sm text-muted-foreground">
          표절 검사 결과를 바탕으로 더 나은 문장 표현을 제안합니다
        </p>
      </CardHeader>

      <CardContent className="space-y-4">
        {!improvementData && !loading && (
          <div className="text-center py-8">
            <Lightbulb className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
            <h3 className="text-lg font-medium mb-2">문장 개선 제안 받기</h3>
            <p className="text-muted-foreground mb-4">
              AI가 분석한 표절 구간과 전체 텍스트를 바탕으로<br />
              더 나은 문장 표현을 제안해드립니다.
            </p>
            <Button onClick={fetchImprovements} disabled={loading}>
              <Sparkles className="h-4 w-4 mr-2" />
              개선 제안 받기
            </Button>
          </div>
        )}

        {loading && (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-muted-foreground">AI가 문장을 분석하고 있습니다...</p>
          </div>
        )}

        {error && (
          <div className="text-center py-8">
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-600">❌ {error}</p>
              <Button 
                variant="outline" 
                className="mt-2" 
                onClick={fetchImprovements}
              >
                다시 시도
              </Button>
            </div>
          </div>
        )}

        {improvementData && (
          <div className="space-y-6">
            {/* 통계 요약 */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Card>
                <CardContent className="p-4 text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {improvementData.total_suggestions}
                  </div>
                  <div className="text-sm text-muted-foreground">총 제안</div>
                </CardContent>
              </Card>
              {Object.entries(improvementData.improvement_categories).slice(0, 3).map(([type, count]) => (
                <Card key={type}>
                  <CardContent className="p-4 text-center">
                    <div className="text-2xl font-bold text-green-600">
                      {count}
                    </div>
                    <div className="text-xs text-muted-foreground">{type}</div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* 개선 제안 목록 */}
            <div className="space-y-4">
              <h4 className="font-semibold flex items-center gap-2">
                <Sparkles className="h-4 w-4" />
                AI 개선 제안 ({improvementData.total_suggestions}개)
              </h4>
              
              {improvementData.suggestions.map((suggestion, index) => (
                <Card key={index} className="border-l-4 border-l-blue-400">
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-2">
                        {getTypeIcon(suggestion.type)}
                        <Badge className={cn("text-xs", getTypeColor(suggestion.type))}>
                          {suggestion.type}
                        </Badge>
                        <span className={cn("text-sm font-medium", getConfidenceColor(suggestion.confidence))}>
                          {suggestion.confidence}% 신뢰도
                        </span>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => copyToClipboard(suggestion.improved_text, index)}
                      >
                        {copiedIndex === index ? (
                          <CheckCircle className="h-4 w-4 text-green-600" />
                        ) : (
                          <Copy className="h-4 w-4" />
                        )}
                      </Button>
                    </div>

                    {/* 원본 → 개선안 */}
                    <div className="space-y-3">
                      <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-xs font-medium text-red-700">원본</span>
                        </div>
                        <p className="text-sm text-red-800">
                          "{suggestion.original_text}"
                        </p>
                      </div>

                      <div className="flex items-center justify-center">
                        <ArrowRight className="h-4 w-4 text-gray-400" />
                      </div>

                      <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-xs font-medium text-green-700">개선안</span>
                          <Sparkles className="h-3 w-3 text-green-600" />
                        </div>
                        <p className="text-sm text-green-800 font-medium">
                          "{suggestion.improved_text}"
                        </p>
                      </div>
                    </div>

                    {/* 설명 */}
                    <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                      <div className="flex items-center gap-2 mb-1">
                        <Info className="h-3 w-3 text-blue-600" />
                        <span className="text-xs font-medium text-blue-700">개선 효과</span>
                      </div>
                      <p className="text-xs text-blue-800">{suggestion.explanation}</p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {improvementData && (
          <div className="flex justify-between items-center pt-4 border-t">
            <div className="text-sm text-muted-foreground">
              💡 제안된 문장을 클릭하여 복사하고 원본 텍스트에 적용해보세요
            </div>
            {onClose && (
              <Button variant="outline" onClick={onClose}>
                닫기
              </Button>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
};