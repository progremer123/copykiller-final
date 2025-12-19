import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Progress } from './ui/progress';
import { Alert, AlertDescription } from './ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { 
    Brain, 
    Lightbulb, 
    Target, 
    TrendingUp, 
    BookOpen, 
    Zap,
    AlertTriangle,
    CheckCircle,
    Crown
} from 'lucide-react';

interface AdvancedAnalysisProps {
    text: string;
    matches: Array<any>;
}

export const AdvancedAnalysis: React.FC<AdvancedAnalysisProps> = ({ text, matches }) => {
    const [loading, setLoading] = useState(false);
    const [analysisData, setAnalysisData] = useState<any>(null);
    const [contextData, setContextData] = useState<any>(null);
    const [suggestions, setSuggestions] = useState<any>(null);

    const runAdvancedAnalysis = async () => {
        setLoading(true);
        try {
            // AI 분석
            const analysisResponse = await fetch('/api/premium/advanced-analysis', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });
            const analysisResult = await analysisResponse.json();
            setAnalysisData(analysisResult.analysis);

            // 맥락 분석
            const contextResponse = await fetch('/api/premium/context-analysis', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text, matches })
            });
            const contextResult = await contextResponse.json();
            setContextData(contextResult.context_analysis);

            // 개선 제안
            const suggestionsResponse = await fetch('/api/premium/improvement-suggestions', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text, matches })
            });
            const suggestionsResult = await suggestionsResponse.json();
            setSuggestions(suggestionsResult.suggestions);

        } catch (error) {
            console.error('Advanced analysis error:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-6">
            {/* 프리미엄 기능 헤더 */}
            <Card className="bg-gradient-to-r from-purple-600 to-blue-600 text-white">
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Crown className="h-6 w-6" />
                        🌟 AI 기반 고급 분석 (프리미엄)
                    </CardTitle>
                    <CardDescription className="text-purple-100">
                        인공지능이 제공하는 차별화된 분석과 개선 제안
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <Button 
                        onClick={runAdvancedAnalysis}
                        disabled={loading || !text}
                        className="bg-white text-purple-600 hover:bg-gray-100"
                    >
                        {loading ? (
                            <>⏳ 분석 중...</>
                        ) : (
                            <>🚀 고급 분석 실행</>
                        )}
                    </Button>
                </CardContent>
            </Card>

            {/* 분석 결과 탭 */}
            {(analysisData || contextData || suggestions) && (
                <Tabs defaultValue="style" className="w-full">
                    <TabsList className="grid w-full grid-cols-3">
                        <TabsTrigger value="style">📊 글쓰기 분석</TabsTrigger>
                        <TabsTrigger value="context">🎯 맥락 분석</TabsTrigger>
                        <TabsTrigger value="suggestions">💡 개선 제안</TabsTrigger>
                    </TabsList>

                    {/* 글쓰기 스타일 분석 */}
                    <TabsContent value="style">
                        {analysisData && (
                            <div className="space-y-4">
                                <Card>
                                    <CardHeader>
                                        <CardTitle className="flex items-center gap-2">
                                            <Brain className="h-5 w-5" />
                                            AI 글쓰기 분석 결과
                                        </CardTitle>
                                    </CardHeader>
                                    <CardContent className="space-y-4">
                                        {/* 기본 통계 */}
                                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                            <div className="text-center p-3 bg-blue-50 rounded-lg">
                                                <div className="text-2xl font-bold text-blue-600">
                                                    {analysisData.sentence_count}
                                                </div>
                                                <div className="text-sm text-gray-600">문장 수</div>
                                            </div>
                                            <div className="text-center p-3 bg-green-50 rounded-lg">
                                                <div className="text-2xl font-bold text-green-600">
                                                    {analysisData.avg_sentence_length?.toFixed(1)}
                                                </div>
                                                <div className="text-sm text-gray-600">평균 문장 길이</div>
                                            </div>
                                            <div className="text-center p-3 bg-purple-50 rounded-lg">
                                                <div className="text-2xl font-bold text-purple-600">
                                                    {analysisData.complexity_score?.toFixed(1)}
                                                </div>
                                                <div className="text-sm text-gray-600">복잡도</div>
                                            </div>
                                            <div className="text-center p-3 bg-orange-50 rounded-lg">
                                                <div className="text-2xl font-bold text-orange-600">
                                                    {analysisData.academic_score?.toFixed(1)}
                                                </div>
                                                <div className="text-sm text-gray-600">학술성 점수</div>
                                            </div>
                                        </div>

                                        {/* 문체 및 어조 */}
                                        <div className="space-y-3">
                                            <h4 className="font-semibold flex items-center gap-2">
                                                <Target className="h-4 w-4" />
                                                감지된 특징
                                            </h4>
                                            <div className="flex flex-wrap gap-2">
                                                <Badge variant="outline">📝 {analysisData.detected_style}</Badge>
                                                <Badge variant="outline">🎵 {analysisData.tone}</Badge>
                                                {analysisData.academic_score > 7 && (
                                                    <Badge className="bg-blue-100 text-blue-700">📚 학술적 글쓰기</Badge>
                                                )}
                                                {analysisData.complexity_score > 8 && (
                                                    <Badge className="bg-purple-100 text-purple-700">🧠 복잡한 문체</Badge>
                                                )}
                                            </div>
                                        </div>

                                        {/* 향상 가능한 영역 */}
                                        {analysisData.improvement_areas && (
                                            <Alert>
                                                <TrendingUp className="h-4 w-4" />
                                                <AlertDescription>
                                                    <strong>향상 포인트:</strong> {analysisData.improvement_areas.join(', ')}
                                                </AlertDescription>
                                            </Alert>
                                        )}
                                    </CardContent>
                                </Card>
                            </div>
                        )}
                    </TabsContent>

                    {/* 맥락 분석 */}
                    <TabsContent value="context">
                        {contextData && (
                            <div className="space-y-4">
                                <Card>
                                    <CardHeader>
                                        <CardTitle className="flex items-center gap-2">
                                            <Target className="h-5 w-5" />
                                            표절 맥락 분석
                                        </CardTitle>
                                    </CardHeader>
                                    <CardContent className="space-y-4">
                                        {/* 위험도 평가 */}
                                        <div className="space-y-3">
                                            <div className="flex items-center justify-between">
                                                <span className="font-medium">위험도 점수</span>
                                                <span className="text-lg font-bold">
                                                    {contextData.risk_score}/10
                                                </span>
                                            </div>
                                            <Progress 
                                                value={contextData.risk_score * 10} 
                                                className={`h-3 ${
                                                    contextData.risk_score >= 7 ? 'bg-red-200' :
                                                    contextData.risk_score >= 4 ? 'bg-yellow-200' : 'bg-green-200'
                                                }`}
                                            />
                                            <Badge 
                                                variant={
                                                    contextData.risk_level === 'high' ? 'destructive' :
                                                    contextData.risk_level === 'medium' ? 'default' : 'secondary'
                                                }
                                                className="flex items-center gap-1"
                                            >
                                                {contextData.risk_level === 'high' ? (
                                                    <><AlertTriangle className="h-3 w-3" /> 높음</>
                                                ) : contextData.risk_level === 'medium' ? (
                                                    <><AlertTriangle className="h-3 w-3" /> 보통</>
                                                ) : (
                                                    <><CheckCircle className="h-3 w-3" /> 낮음</>
                                                )}
                                            </Badge>
                                        </div>

                                        {/* 표절 유형 */}
                                        {contextData.plagiarism_types && (
                                            <div className="space-y-2">
                                                <h4 className="font-semibold">감지된 표절 유형</h4>
                                                <div className="flex flex-wrap gap-2">
                                                    {contextData.plagiarism_types.map((type: string, index: number) => (
                                                        <Badge key={index} variant="outline">
                                                            {type}
                                                        </Badge>
                                                    ))}
                                                </div>
                                            </div>
                                        )}

                                        {/* 법적 위험도 */}
                                        {contextData.legal_assessment && (
                                            <Alert className={
                                                contextData.legal_assessment.includes('높음') ? 'border-red-200 bg-red-50' :
                                                contextData.legal_assessment.includes('보통') ? 'border-yellow-200 bg-yellow-50' :
                                                'border-green-200 bg-green-50'
                                            }>
                                                <AlertDescription>
                                                    <strong>법적 위험도:</strong> {contextData.legal_assessment}
                                                </AlertDescription>
                                            </Alert>
                                        )}
                                    </CardContent>
                                </Card>
                            </div>
                        )}
                    </TabsContent>

                    {/* 개선 제안 */}
                    <TabsContent value="suggestions">
                        {suggestions && (
                            <div className="space-y-4">
                                <Card>
                                    <CardHeader>
                                        <CardTitle className="flex items-center gap-2">
                                            <Lightbulb className="h-5 w-5" />
                                            실시간 개선 제안
                                        </CardTitle>
                                    </CardHeader>
                                    <CardContent className="space-y-6">
                                        {/* 동의어 제안 */}
                                        {suggestions.synonym_suggestions && suggestions.synonym_suggestions.length > 0 && (
                                            <div className="space-y-3">
                                                <h4 className="font-semibold flex items-center gap-2">
                                                    🔄 동의어 제안
                                                </h4>
                                                <div className="space-y-2">
                                                    {suggestions.synonym_suggestions.map((suggestion: any, index: number) => (
                                                        <div key={index} className="p-3 bg-blue-50 rounded-lg">
                                                            <div className="font-medium text-blue-800">
                                                                "{suggestion.original}" → "{suggestion.alternatives.join(', ')}"
                                                            </div>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        )}

                                        {/* 문장 재구성 */}
                                        {suggestions.restructuring_suggestions && suggestions.restructuring_suggestions.length > 0 && (
                                            <div className="space-y-3">
                                                <h4 className="font-semibold flex items-center gap-2">
                                                    📝 문장 재구성 제안
                                                </h4>
                                                <div className="space-y-3">
                                                    {suggestions.restructuring_suggestions.map((suggestion: any, index: number) => (
                                                        <div key={index} className="p-4 bg-green-50 rounded-lg border border-green-200">
                                                            <div className="space-y-2">
                                                                <div>
                                                                    <span className="font-medium text-green-800">원문:</span>
                                                                    <p className="text-gray-700 mt-1">{suggestion.original}</p>
                                                                </div>
                                                                <div>
                                                                    <span className="font-medium text-green-800">개선안:</span>
                                                                    <p className="text-green-700 mt-1">{suggestion.improved}</p>
                                                                </div>
                                                                <div className="text-sm text-green-600">
                                                                    💡 {suggestion.reason}
                                                                </div>
                                                            </div>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        )}

                                        {/* 인용 가이드 */}
                                        {suggestions.citation_guide && (
                                            <div className="space-y-3">
                                                <h4 className="font-semibold flex items-center gap-2">
                                                    📚 인용 가이드
                                                </h4>
                                                <Alert className="bg-purple-50 border-purple-200">
                                                    <BookOpen className="h-4 w-4" />
                                                    <AlertDescription>
                                                        {suggestions.citation_guide}
                                                    </AlertDescription>
                                                </Alert>
                                            </div>
                                        )}

                                        {/* 패러프레이징 예시 */}
                                        {suggestions.paraphrasing_examples && suggestions.paraphrasing_examples.length > 0 && (
                                            <div className="space-y-3">
                                                <h4 className="font-semibold flex items-center gap-2">
                                                    ✏️ 패러프레이징 예시
                                                </h4>
                                                <div className="space-y-3">
                                                    {suggestions.paraphrasing_examples.map((example: any, index: number) => (
                                                        <div key={index} className="p-4 bg-orange-50 rounded-lg border border-orange-200">
                                                            <div className="space-y-2">
                                                                <div>
                                                                    <span className="font-medium text-orange-800">원본:</span>
                                                                    <p className="text-gray-700 mt-1">{example.original}</p>
                                                                </div>
                                                                <div>
                                                                    <span className="font-medium text-orange-800">패러프레이징:</span>
                                                                    <p className="text-orange-700 mt-1">{example.paraphrased}</p>
                                                                </div>
                                                                <div className="text-sm text-orange-600">
                                                                    📝 기법: {example.technique}
                                                                </div>
                                                            </div>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        )}
                                    </CardContent>
                                </Card>
                            </div>
                        )}
                    </TabsContent>
                </Tabs>
            )}

            {/* 차별화 포인트 안내 */}
            <Card className="border-2 border-dashed border-blue-200">
                <CardHeader>
                    <CardTitle className="text-blue-600 flex items-center gap-2">
                        <Zap className="h-5 w-5" />
                        🆚 다른 표절검사기와의 차별점
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <h5 className="font-semibold text-red-600">❌ 기존 서비스</h5>
                            <ul className="text-sm space-y-1 text-gray-600">
                                <li>• 단순 유사도만 측정</li>
                                <li>• 결과만 보여줌</li>
                                <li>• 사후 검사만 가능</li>
                                <li>• 기계적 판단</li>
                            </ul>
                        </div>
                        <div className="space-y-2">
                            <h5 className="font-semibold text-green-600">✅ 우리 서비스</h5>
                            <ul className="text-sm space-y-1 text-gray-600">
                                <li>• AI 기반 맥락 분석</li>
                                <li>• 구체적 개선 방법 제시</li>
                                <li>• 실시간 작성 도움</li>
                                <li>• 지능적 맥락 이해</li>
                            </ul>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
};