import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
    Crown, 
    Brain, 
    Lightbulb, 
    Target, 
    Zap, 
    CheckCircle,
    Star,
    Sparkles,
    Rocket
} from 'lucide-react';

interface PremiumFeaturesProps {}

export const PremiumFeatures: React.FC<PremiumFeaturesProps> = () => {
    const [featuresData, setFeaturesData] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [demoLoading, setDemoLoading] = useState(false);
    const [demoResult, setDemoResult] = useState<any>(null);

    useEffect(() => {
        fetchPremiumFeatures();
    }, []);

    const fetchPremiumFeatures = async () => {
        try {
            const response = await fetch('/api/premium/premium-features');
            const data = await response.json();
            setFeaturesData(data);
        } catch (error) {
            console.error('Failed to fetch premium features:', error);
        } finally {
            setLoading(false);
        }
    };

    const runPremiumDemo = async () => {
        setDemoLoading(true);
        try {
            // 샘플 텍스트로 프리미엄 기능 데모 실행
            const sampleText = "인공지능은 현대 기술의 핵심입니다. 머신러닝과 딥러닝을 통해 컴퓨터가 학습하고 판단할 수 있게 됩니다. 자연어 처리, 이미지 인식, 음성 인식 등 다양한 분야에 활용되고 있습니다.";
            
            const sampleMatches = [
                { text: "인공지능은 현대 기술의 핵심입니다", source: "AI 기술 개요", similarity: 75.0, startIndex: 0, endIndex: 20 },
                { text: "머신러닝과 딥러닝", source: "기계학습 논문", similarity: 65.0, startIndex: 22, endIndex: 35 }
            ];

            // AI 분석
            const analysisResponse = await fetch('http://localhost:8006/api/premium/advanced-analysis', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: sampleText })
            });
            const analysisResult = await analysisResponse.json();

            // 맥락 분석
            const contextResponse = await fetch('http://localhost:8006/api/premium/context-analysis', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: sampleText, matches: sampleMatches })
            });
            const contextResult = await contextResponse.json();

            // 개선 제안
            const suggestionResponse = await fetch('http://localhost:8006/api/premium/improvement-suggestions', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: sampleText, matches: sampleMatches })
            });
            const suggestionResult = await suggestionResponse.json();

            setDemoResult({
                analysis: analysisResult.analysis,
                context: contextResult.context_analysis,
                suggestions: suggestionResult.suggestions
            });
        } catch (error) {
            console.error('Demo failed:', error);
            alert('데모 실행 중 오류가 발생했습니다. 백엔드 서버가 실행중인지 확인해주세요.');
        } finally {
            setDemoLoading(false);
        }
    };

    if (loading) {
        return (
            <Card>
                <CardContent className="p-8 text-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
                    <p className="mt-4 text-muted-foreground">프리미엄 기능 로딩 중...</p>
                </CardContent>
            </Card>
        );
    }

    if (!featuresData) {
        return (
            <Alert>
                <AlertDescription>프리미엄 기능 정보를 불러올 수 없습니다.</AlertDescription>
            </Alert>
        );
    }

    return (
        <div className="space-y-8">
            {/* Hero Section */}
            <Card className="bg-gradient-to-r from-purple-600 to-blue-600 text-white overflow-hidden relative">
                <div className="absolute inset-0 bg-black/10"></div>
                <CardHeader className="relative z-10">
                    <CardTitle className="text-3xl font-bold flex items-center gap-3">
                        <Crown className="h-10 w-10" />
                        🌟 AI 기반 프리미엄 표절 분석
                    </CardTitle>
                    <p className="text-xl text-purple-100">
                        단순한 비교를 넘어선, 인공지능이 제공하는 차별화된 분석 경험
                    </p>
                </CardHeader>
                <CardContent className="relative z-10">
                    <div className="flex flex-wrap gap-2 mb-6">
                        <Badge className="bg-white/20 text-white border-white/30">
                            🚀 차세대 기술
                        </Badge>
                        <Badge className="bg-white/20 text-white border-white/30">
                            🤖 AI 분석
                        </Badge>
                        <Badge className="bg-white/20 text-white border-white/30">
                            💡 실시간 개선
                        </Badge>
                        <Badge className="bg-white/20 text-white border-white/30">
                            🎯 맥락 이해
                        </Badge>
                    </div>
                    <Button 
                        size="lg" 
                        className="bg-white text-purple-600 hover:bg-gray-100"
                        onClick={runPremiumDemo}
                        disabled={demoLoading}
                    >
                        {demoLoading ? (
                            <>
                                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-purple-600 mr-2"></div>
                                체험 실행 중...
                            </>
                        ) : (
                            <>
                                <Sparkles className="h-5 w-5 mr-2" />
                                프리미엄 체험하기
                            </>
                        )}
                    </Button>
                </CardContent>
            </Card>

            {/* Features Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* AI Analysis */}
                <Card className="border-2 border-blue-200 hover:border-blue-300 transition-colors">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-3 text-blue-600">
                            <Brain className="h-6 w-6" />
                            {featuresData.premium_features.ai_analysis.name}
                        </CardTitle>
                        <p className="text-muted-foreground">
                            {featuresData.premium_features.ai_analysis.description}
                        </p>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-3">
                            <h4 className="font-semibold text-sm">핵심 혜택:</h4>
                            <ul className="space-y-2">
                                {featuresData.premium_features.ai_analysis.benefits.map((benefit: string, index: number) => (
                                    <li key={index} className="flex items-center gap-2 text-sm">
                                        <CheckCircle className="h-4 w-4 text-green-500" />
                                        {benefit}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </CardContent>
                </Card>

                {/* Smart Suggestions */}
                <Card className="border-2 border-green-200 hover:border-green-300 transition-colors">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-3 text-green-600">
                            <Lightbulb className="h-6 w-6" />
                            {featuresData.premium_features.smart_suggestions.name}
                        </CardTitle>
                        <p className="text-muted-foreground">
                            {featuresData.premium_features.smart_suggestions.description}
                        </p>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-3">
                            <h4 className="font-semibold text-sm">핵심 혜택:</h4>
                            <ul className="space-y-2">
                                {featuresData.premium_features.smart_suggestions.benefits.map((benefit: string, index: number) => (
                                    <li key={index} className="flex items-center gap-2 text-sm">
                                        <CheckCircle className="h-4 w-4 text-green-500" />
                                        {benefit}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </CardContent>
                </Card>

                {/* Context Analysis */}
                <Card className="border-2 border-purple-200 hover:border-purple-300 transition-colors">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-3 text-purple-600">
                            <Target className="h-6 w-6" />
                            {featuresData.premium_features.context_analysis.name}
                        </CardTitle>
                        <p className="text-muted-foreground">
                            {featuresData.premium_features.context_analysis.description}
                        </p>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-3">
                            <h4 className="font-semibold text-sm">핵심 혜택:</h4>
                            <ul className="space-y-2">
                                {featuresData.premium_features.context_analysis.benefits.map((benefit: string, index: number) => (
                                    <li key={index} className="flex items-center gap-2 text-sm">
                                        <CheckCircle className="h-4 w-4 text-green-500" />
                                        {benefit}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </CardContent>
                </Card>

                {/* Real-time Help */}
                <Card className="border-2 border-orange-200 hover:border-orange-300 transition-colors">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-3 text-orange-600">
                            <Zap className="h-6 w-6" />
                            {featuresData.premium_features.real_time_help.name}
                        </CardTitle>
                        <p className="text-muted-foreground">
                            {featuresData.premium_features.real_time_help.description}
                        </p>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-3">
                            <h4 className="font-semibold text-sm">핵심 혜택:</h4>
                            <ul className="space-y-2">
                                {featuresData.premium_features.real_time_help.benefits.map((benefit: string, index: number) => (
                                    <li key={index} className="flex items-center gap-2 text-sm">
                                        <CheckCircle className="h-4 w-4 text-green-500" />
                                        {benefit}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Differentiation Section */}
            <Card className="border-2 border-dashed border-gray-300">
                <CardHeader>
                    <CardTitle className="flex items-center gap-3">
                        <Rocket className="h-6 w-6" />
                        🆚 경쟁력 있는 차별화 포인트
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="space-y-4">
                        {featuresData.differentiation.map((point: string, index: number) => (
                            <div key={index} className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
                                <Star className="h-5 w-5 text-blue-500 mt-0.5 flex-shrink-0" />
                                <p className="text-sm text-blue-800">{point}</p>
                            </div>
                        ))}
                    </div>
                </CardContent>
            </Card>

            {/* Demo Results */}
            {demoResult && (
                <Card className="border-2 border-purple-200 bg-purple-50">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-3 text-purple-600">
                            <Sparkles className="h-6 w-6" />
                            🎯 프리미엄 체험 결과
                        </CardTitle>
                        <p className="text-purple-700">
                            샘플 텍스트를 통한 AI 기반 고급 분석 결과입니다
                        </p>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        {/* AI 분석 결과 */}
                        {demoResult.analysis && (
                            <div className="bg-white p-4 rounded-lg border border-purple-200">
                                <h4 className="font-semibold text-purple-800 mb-3 flex items-center gap-2">
                                    <Brain className="h-4 w-4" />
                                    AI 글쓰기 분석 결과
                                </h4>
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                                    <div className="text-center p-2 bg-blue-50 rounded">
                                        <div className="font-bold text-blue-600">{demoResult.analysis.sentence_count}</div>
                                        <div className="text-gray-600">문장 수</div>
                                    </div>
                                    <div className="text-center p-2 bg-green-50 rounded">
                                        <div className="font-bold text-green-600">{demoResult.analysis.word_count}</div>
                                        <div className="text-gray-600">단어 수</div>
                                    </div>
                                    <div className="text-center p-2 bg-purple-50 rounded">
                                        <div className="font-bold text-purple-600">{demoResult.analysis.complexity_score}</div>
                                        <div className="text-gray-600">복잡도</div>
                                    </div>
                                    <div className="text-center p-2 bg-orange-50 rounded">
                                        <div className="font-bold text-orange-600">{demoResult.analysis.academic_score}</div>
                                        <div className="text-gray-600">학술성</div>
                                    </div>
                                </div>
                                <div className="mt-3 flex gap-2 flex-wrap">
                                    <Badge variant="outline">📝 {demoResult.analysis.detected_style}</Badge>
                                    <Badge variant="outline">🎵 {demoResult.analysis.tone}</Badge>
                                </div>
                            </div>
                        )}

                        {/* 맥락 분석 결과 */}
                        {demoResult.context && (
                            <div className="bg-white p-4 rounded-lg border border-purple-200">
                                <h4 className="font-semibold text-purple-800 mb-3 flex items-center gap-2">
                                    <Target className="h-4 w-4" />
                                    맥락 분석 결과
                                </h4>
                                <div className="space-y-2">
                                    <div className="flex justify-between items-center">
                                        <span>위험도 점수:</span>
                                        <Badge variant={demoResult.context.risk_score >= 7 ? "destructive" : demoResult.context.risk_score >= 4 ? "default" : "secondary"}>
                                            {demoResult.context.risk_score}/10
                                        </Badge>
                                    </div>
                                    <div className="text-sm text-gray-600">
                                        법적 평가: {demoResult.context.legal_assessment}
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* 개선 제안 */}
                        {demoResult.suggestions && (
                            <div className="bg-white p-4 rounded-lg border border-purple-200">
                                <h4 className="font-semibold text-purple-800 mb-3 flex items-center gap-2">
                                    <Lightbulb className="h-4 w-4" />
                                    개선 제안
                                </h4>
                                <div className="space-y-3 text-sm">
                                    {demoResult.suggestions.synonym_suggestions && demoResult.suggestions.synonym_suggestions.length > 0 && (
                                        <div>
                                            <span className="font-medium text-blue-800">🔄 동의어 제안: </span>
                                            <span className="text-gray-700">
                                                {demoResult.suggestions.synonym_suggestions.length}개 단어 개선 가능
                                            </span>
                                        </div>
                                    )}
                                    {demoResult.suggestions.citation_guide && (
                                        <div>
                                            <span className="font-medium text-green-800">📚 인용 가이드: </span>
                                            <span className="text-gray-700">
                                                {demoResult.suggestions.citation_guide.substring(0, 100)}...
                                            </span>
                                        </div>
                                    )}
                                    {demoResult.suggestions.paraphrasing_examples && demoResult.suggestions.paraphrasing_examples.length > 0 && (
                                        <div>
                                            <span className="font-medium text-orange-800">✏️ 패러프레이징: </span>
                                            <span className="text-gray-700">
                                                {demoResult.suggestions.paraphrasing_examples.length}개 개선 예시 제공
                                            </span>
                                        </div>
                                    )}
                                </div>
                            </div>
                        )}

                        <Alert className="bg-purple-100 border-purple-300">
                            <CheckCircle className="h-4 w-4" />
                            <AlertDescription className="text-purple-800">
                                <strong>🎉 체험 완료!</strong> 이것은 실제 프리미엄 기능의 일부입니다. 
                                전체 기능을 이용하려면 프리미엄을 시작해보세요.
                            </AlertDescription>
                        </Alert>
                    </CardContent>
                </Card>
            )}

            {/* Call to Action */}
            <Card className="bg-gradient-to-r from-green-500 to-blue-500 text-white text-center">
                <CardContent className="p-8">
                    <h3 className="text-2xl font-bold mb-4">
                        🚀 지금 차별화된 표절검사를 경험해보세요!
                    </h3>
                    <p className="text-lg mb-6 text-green-100">
                        AI가 제공하는 스마트한 분석과 개선 제안으로<br/>
                        더 나은 글쓰기를 시작하세요
                    </p>
                    <div className="space-x-4">
                        <Button size="lg" className="bg-white text-green-600 hover:bg-gray-100">
                            <Crown className="h-5 w-5 mr-2" />
                            프리미엄 시작하기
                        </Button>
                        <Button size="lg" variant="outline" className="border-white text-white hover:bg-white/10">
                            더 알아보기
                        </Button>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
};