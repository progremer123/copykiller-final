import React, { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { 
  Shield, 
  FileText, 
  Zap, 
  CheckCircle, 
  AlertTriangle, 
  TrendingDown,
  Eye,
  EyeOff,
  RotateCcw,
  Copy,
  Download,
  ChevronDown,
  ChevronUp,
  Brain,
  Target,
  BarChart3
} from "lucide-react";
import { toast } from "sonner";

interface AvoidanceModification {
  type: string;
  original_text: string;
  modified_text: string;
  start_index: number;
  end_index: number;
  reason: string;
  confidence: number;
}

interface AvoidanceResult {
  success: boolean;
  needs_rewriting?: boolean;
  original_text: string;
  rewritten_text: string;
  similarity_reduction: number;
  confidence_score: number;
  modifications: AvoidanceModification[];
  plagiarism_check?: {
    original_similarity: number;
    total_matches: number;
    high_risk_matches: number;
    estimated_new_similarity: number;
  };
  statistics: {
    total_modifications: number;
    plagiarism_rewrites: number;
    general_variations: number;
  };
  message: string;
}

interface SystemCapabilities {
  success: boolean;
  system_info: {
    name: string;
    description: string;
    version: string;
    author: string;
  };
  capabilities: {
    total_synonyms: number;
    structure_patterns: number;
    expression_variations: number;
  };
  usage_guide: string[];
  features: string[];
}

interface AIPlagiarismAvoidanceProps {
  checkId?: string;
  initialText?: string;
  onAvoidanceComplete?: (result: AvoidanceResult) => void;
}

const AIPlagiarismAvoidance: React.FC<AIPlagiarismAvoidanceProps> = ({
  checkId,
  initialText = "",
  onAvoidanceComplete
}) => {
  const [inputText, setInputText] = useState(initialText);
  const [similarityThreshold, setSimilarityThreshold] = useState(30.0);
  const [avoidanceResult, setAvoidanceResult] = useState<AvoidanceResult | null>(null);
  const [systemCapabilities, setSystemCapabilities] = useState<SystemCapabilities | null>(null);
  const [loading, setLoading] = useState(false);
  const [showComparison, setShowComparison] = useState(true);
  const [showModifications, setShowModifications] = useState(true);
  const [activeTab, setActiveTab] = useState(checkId ? "existing" : "direct");
  const [showResultModal, setShowResultModal] = useState(false);

  useEffect(() => {
    fetchSystemCapabilities();
  }, []);

  const fetchSystemCapabilities = async () => {
    try {
      const response = await fetch("/api/avoid-plagiarism/capabilities");
      if (response.ok) {
        const data = await response.json();
        setSystemCapabilities(data);
      }
    } catch (error) {
      console.error("시스템 능력 조회 오류:", error);
    }
  };

  const handleAvoidPlagiarismExisting = async () => {
    if (!checkId) {
      toast.error("표절 검사 ID가 필요합니다");
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`/api/avoid-plagiarism/${checkId}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      setAvoidanceResult(result);
      setShowResultModal(true); // ✅ 모달 열기
      
      if (onAvoidanceComplete) {
        onAvoidanceComplete(result);
      }

      toast.success(result.message || "표절 회피 완료!");
    } catch (error) {
      console.error("표절 회피 오류:", error);
      toast.error("표절 회피 중 오류가 발생했습니다");
    } finally {
      setLoading(false);
    }
  };

  const handleAvoidPlagiarismDirect = async () => {
    if (!inputText.trim()) {
      toast.error("텍스트를 입력해주세요");
      return;
    }

    if (inputText.trim().length < 10) {
      toast.error("최소 10자 이상 입력해주세요");
      return;
    }

    setLoading(true);
    try {
      const response = await fetch("/api/avoid-plagiarism/text", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text: inputText,
          similarity_threshold: similarityThreshold
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      setAvoidanceResult(result);
      setShowResultModal(true); // ✅ 모달 열기
      
      if (onAvoidanceComplete) {
        onAvoidanceComplete(result);
      }

      if (result.needs_rewriting) {
        toast.success(result.message || "표절 회피 완료!");
      } else {
        toast.success(result.message || "표절 위험이 낮습니다!");
      }
    } catch (error) {
      console.error("직접 텍스트 표절 회피 오류:", error);
      toast.error("표절 회피 중 오류가 발생했습니다");
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      toast.success("텍스트가 클립보드에 복사되었습니다");
    } catch (error) {
      toast.error("복사에 실패했습니다");
    }
  };

  const downloadText = (text: string, filename: string) => {
    const element = document.createElement("a");
    const file = new Blob([text], { type: "text/plain" });
    element.href = URL.createObjectURL(file);
    element.download = filename;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const resetForm = () => {
    setInputText(initialText);
    setAvoidanceResult(null);
    setSimilarityThreshold(30.0);
  };

  const getModificationTypeColor = (type: string) => {
    switch (type) {
      case "plagiarism_rewrite":
        return "destructive";
      case "general_variation":
        return "secondary";
      default:
        return "outline";
    }
  };

  const getModificationTypeIcon = (type: string) => {
    switch (type) {
      case "plagiarism_rewrite":
        return <Shield className="h-3 w-3" />;
      case "general_variation":
        return <Zap className="h-3 w-3" />;
      default:
        return <FileText className="h-3 w-3" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* 헤더 섹션 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-blue-600" />
            AI 표절 회피 시스템
          </CardTitle>
          <CardDescription>
            AI가 표절 위험 텍스트를 자동으로 감지하고 재작성하여 유사도를 낮춥니다
          </CardDescription>
        </CardHeader>
        {systemCapabilities && (
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-3 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {systemCapabilities.capabilities.total_synonyms}
                </div>
                <div className="text-sm text-gray-600">동의어 사전</div>
              </div>
              <div className="text-center p-3 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {systemCapabilities.capabilities.structure_patterns}
                </div>
                <div className="text-sm text-gray-600">구조 패턴</div>
              </div>
              <div className="text-center p-3 bg-purple-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">
                  {systemCapabilities.capabilities.expression_variations}
                </div>
                <div className="text-sm text-gray-600">표현 변형</div>
              </div>
            </div>
          </CardContent>
        )}
      </Card>

      {/* 메인 탭 섹션 */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="existing" disabled={!checkId}>
            <Target className="h-4 w-4 mr-2" />
            기존 검사 결과
          </TabsTrigger>
          <TabsTrigger value="direct">
            <FileText className="h-4 w-4 mr-2" />
            직접 텍스트 입력
          </TabsTrigger>
        </TabsList>

        {/* 기존 검사 결과 탭 */}
        <TabsContent value="existing">
          <Card>
            <CardHeader>
              <CardTitle>표절 검사 결과 기반 회피</CardTitle>
              <CardDescription>
                기존 표절 검사 결과를 바탕으로 표절 부분을 자동 재작성합니다
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {checkId ? (
                <>
                  <div className="p-3 bg-gray-50 rounded-lg">
                    <div className="text-sm font-medium">검사 ID: {checkId}</div>
                  </div>
                  <div className="flex gap-2">
                    <Button 
                      onClick={handleAvoidPlagiarismExisting}
                      disabled={loading}
                      className="flex-1"
                    >
                      {loading ? (
                        <>
                          <RotateCcw className="h-4 w-4 mr-2 animate-spin" />
                          표절 회피 처리 중...
                        </>
                      ) : (
                        <>
                          <Shield className="h-4 w-4 mr-2" />
                          AI 표절 회피 실행
                        </>
                      )}
                    </Button>
                    {avoidanceResult && (
                      <Button 
                        variant="default"
                        onClick={() => setShowResultModal(true)}
                        className="bg-green-600 hover:bg-green-700"
                      >
                        <Eye className="h-4 w-4 mr-2" />
                        결과 보기
                      </Button>
                    )}
                  </div>
                </>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  표절 검사 ID가 필요합니다
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* 직접 텍스트 입력 탭 */}
        <TabsContent value="direct">
          <Card>
            <CardHeader>
              <CardTitle>직접 텍스트 입력</CardTitle>
              <CardDescription>
                텍스트를 직접 입력하여 표절 검사 후 자동 회피 처리합니다
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="input-text">분석할 텍스트</Label>
                <Textarea
                  id="input-text"
                  placeholder="분석하고 싶은 텍스트를 입력하세요... (최소 10자)"
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  rows={6}
                />
                <div className="text-sm text-gray-500">
                  현재 길이: {inputText.length}자
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="threshold">유사도 임계값 (%)</Label>
                <Input
                  id="threshold"
                  type="number"
                  min="10"
                  max="90"
                  step="5"
                  value={similarityThreshold}
                  onChange={(e) => setSimilarityThreshold(parseFloat(e.target.value))}
                />
                <div className="text-sm text-gray-500">
                  {similarityThreshold}% 이상 유사한 부분을 재작성합니다
                </div>
              </div>

              <div className="flex gap-2">
                <Button 
                  onClick={handleAvoidPlagiarismDirect}
                  disabled={loading || inputText.trim().length < 10}
                  className="flex-1"
                >
                  {loading ? (
                    <>
                      <RotateCcw className="h-4 w-4 mr-2 animate-spin" />
                      분석 중...
                    </>
                  ) : (
                    <>
                      <Brain className="h-4 w-4 mr-2" />
                      AI 표절 회피 실행
                    </>
                  )}
                </Button>
                {avoidanceResult && (
                  <Button 
                    variant="default"
                    onClick={() => setShowResultModal(true)}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    <Eye className="h-4 w-4 mr-2" />
                    결과 보기
                  </Button>
                )}
                <Button variant="outline" onClick={resetForm}>
                  <RotateCcw className="h-4 w-4 mr-2" />
                  초기화
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* ✅ 결과 모달 */}
      <Dialog open={showResultModal} onOpenChange={setShowResultModal}>
        <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-2xl">
              <Shield className="h-6 w-6 text-green-600" />
              AI 표절 회피 분석 결과
            </DialogTitle>
            <DialogDescription>
              텍스트가 AI에 의해 자동으로 재작성되었습니다
            </DialogDescription>
          </DialogHeader>

          {avoidanceResult && (
            <div className="space-y-6 mt-4">
          {/* 요약 통계 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5 text-green-600" />
                처리 결과 요약
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">
                    {avoidanceResult.similarity_reduction.toFixed(1)}%
                  </div>
                  <div className="text-sm text-gray-600">유사도 감소</div>
                </div>
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">
                    {avoidanceResult.confidence_score.toFixed(1)}%
                  </div>
                  <div className="text-sm text-gray-600">신뢰도</div>
                </div>
                <div className="text-center p-4 bg-purple-50 rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">
                    {avoidanceResult.statistics.total_modifications}
                  </div>
                  <div className="text-sm text-gray-600">총 수정사항</div>
                </div>
                <div className="text-center p-4 bg-orange-50 rounded-lg">
                  <div className="text-2xl font-bold text-orange-600">
                    {avoidanceResult.statistics.plagiarism_rewrites}
                  </div>
                  <div className="text-sm text-gray-600">표절 재작성</div>
                </div>
              </div>

              {avoidanceResult.plagiarism_check && (
                <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                  <div className="flex justify-between items-center mb-2">
                    <span className="font-medium">유사도 변화</span>
                    <Badge variant="outline">
                      <TrendingDown className="h-3 w-3 mr-1" />
                      -{avoidanceResult.similarity_reduction.toFixed(1)}%
                    </Badge>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>원본 유사도:</span>
                      <span className="text-red-600 font-medium">
                        {avoidanceResult.plagiarism_check.original_similarity.toFixed(1)}%
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>예상 새 유사도:</span>
                      <span className="text-green-600 font-medium">
                        {avoidanceResult.plagiarism_check.estimated_new_similarity.toFixed(1)}%
                      </span>
                    </div>
                    <Progress 
                      value={avoidanceResult.plagiarism_check.estimated_new_similarity} 
                      className="h-2"
                    />
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* 텍스트 비교 - 개선된 가독성 */}
          <Card className="shadow-lg">
            <CardHeader className="bg-gradient-to-r from-blue-50 to-purple-50">
              <CardTitle className="flex items-center justify-between">
                <span className="flex items-center gap-2">
                  <Eye className="h-6 w-6 text-blue-600" />
                  <span className="text-xl">텍스트 전후 비교</span>
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowComparison(!showComparison)}
                >
                  {showComparison ? (
                    <>
                      <EyeOff className="h-4 w-4 mr-2" />
                      숨기기
                    </>
                  ) : (
                    <>
                      <Eye className="h-4 w-4 mr-2" />
                      보기
                    </>
                  )}
                </Button>
              </CardTitle>
              <CardDescription className="text-base mt-2">
                AI가 표절 위험 부분을 자동으로 재작성한 결과를 확인하세요
              </CardDescription>
            </CardHeader>
            {showComparison && (
              <CardContent className="pt-6">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* 원본 텍스트 */}
                  <div className="space-y-3">
                    <div className="flex items-center justify-between pb-2 border-b-2 border-red-200">
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-red-500"></div>
                        <Label className="text-lg font-bold text-red-700">원본 텍스트</Label>
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => copyToClipboard(avoidanceResult.original_text)}
                        className="hover:bg-red-50"
                      >
                        <Copy className="h-3 w-3 mr-1" />
                        복사
                      </Button>
                    </div>
                    <div className="bg-red-50 border-2 border-red-200 rounded-lg">
                      <ScrollArea className="h-64 w-full p-5">
                        <div className="text-base leading-relaxed text-gray-800 whitespace-pre-wrap font-medium">
                          {avoidanceResult.original_text}
                        </div>
                      </ScrollArea>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-red-600">
                      <AlertTriangle className="h-4 w-4" />
                      <span>표절 위험 부분 포함</span>
                    </div>
                  </div>

                  {/* 재작성된 텍스트 */}
                  <div className="space-y-3">
                    <div className="flex items-center justify-between pb-2 border-b-2 border-green-200">
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-green-500"></div>
                        <Label className="text-lg font-bold text-green-700">재작성된 텍스트</Label>
                      </div>
                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => copyToClipboard(avoidanceResult.rewritten_text)}
                          className="hover:bg-green-50"
                        >
                          <Copy className="h-3 w-3 mr-1" />
                          복사
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => downloadText(
                            avoidanceResult.rewritten_text, 
                            "plagiarism_avoided_text.txt"
                          )}
                          className="hover:bg-green-50"
                        >
                          <Download className="h-3 w-3 mr-1" />
                          다운
                        </Button>
                      </div>
                    </div>
                    <div className="bg-green-50 border-2 border-green-200 rounded-lg">
                      <ScrollArea className="h-64 w-full p-5">
                        <div className="text-base leading-relaxed text-gray-800 whitespace-pre-wrap font-medium">
                          {avoidanceResult.rewritten_text}
                        </div>
                      </ScrollArea>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-green-600">
                      <CheckCircle className="h-4 w-4" />
                      <span>표절 위험 감소됨</span>
                    </div>
                  </div>
                </div>

                {/* 변경사항 요약 */}
                <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-green-50 rounded-lg border-2 border-blue-200">
                  <div className="flex items-center gap-2 mb-3">
                    <Target className="h-5 w-5 text-blue-600" />
                    <span className="font-bold text-lg">주요 변경사항</span>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
                    <div className="bg-white p-3 rounded-lg shadow-sm">
                      <div className="text-2xl font-bold text-blue-600">
                        {avoidanceResult.modifications.length}
                      </div>
                      <div className="text-sm text-gray-600">개 부분 수정</div>
                    </div>
                    <div className="bg-white p-3 rounded-lg shadow-sm">
                      <div className="text-2xl font-bold text-green-600">
                        {avoidanceResult.similarity_reduction.toFixed(0)}%
                      </div>
                      <div className="text-sm text-gray-600">유사도 감소</div>
                    </div>
                    <div className="bg-white p-3 rounded-lg shadow-sm">
                      <div className="text-2xl font-bold text-purple-600">
                        {avoidanceResult.confidence_score.toFixed(0)}%
                      </div>
                      <div className="text-sm text-gray-600">신뢰도</div>
                    </div>
                  </div>
                </div>
              </CardContent>
            )}
          </Card>

          {/* 수정사항 상세 - 개선된 가독성 */}
          {avoidanceResult.modifications.length > 0 && (
            <Card className="shadow-lg">
              <CardHeader className="bg-gradient-to-r from-yellow-50 to-orange-50">
                <CardTitle className="flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    <Zap className="h-6 w-6 text-yellow-600" />
                    <span className="text-xl">상세 수정사항</span>
                    <Badge variant="secondary" className="text-base px-3 py-1">
                      {avoidanceResult.modifications.length}개
                    </Badge>
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowModifications(!showModifications)}
                  >
                    {showModifications ? (
                      <>
                        <ChevronUp className="h-4 w-4 mr-2" />
                        접기
                      </>
                    ) : (
                      <>
                        <ChevronDown className="h-4 w-4 mr-2" />
                        펼치기
                      </>
                    )}
                  </Button>
                </CardTitle>
                <CardDescription className="text-base mt-2">
                  각 수정 부분을 자세히 확인하고 어떻게 변경되었는지 비교해보세요
                </CardDescription>
              </CardHeader>
              <Collapsible open={showModifications} onOpenChange={setShowModifications}>
                <CollapsibleContent>
                  <CardContent className="pt-6">
                    <ScrollArea className="h-96 w-full pr-4">
                      <div className="space-y-4">
                        {avoidanceResult.modifications.map((modification, index) => (
                          <div 
                            key={index} 
                            className="border-2 border-gray-200 rounded-xl p-5 space-y-4 hover:shadow-md transition-shadow bg-white"
                          >
                            {/* 헤더 */}
                            <div className="flex items-center justify-between pb-3 border-b">
                              <div className="flex items-center gap-3">
                                <div className="flex items-center justify-center w-8 h-8 rounded-full bg-blue-100 text-blue-600 font-bold">
                                  {index + 1}
                                </div>
                                <Badge 
                                  variant={getModificationTypeColor(modification.type)}
                                  className="text-sm px-3 py-1"
                                >
                                  {getModificationTypeIcon(modification.type)}
                                  <span className="ml-1">
                                    {modification.type === "plagiarism_rewrite" ? "표절 재작성" : "일반 변형"}
                                  </span>
                                </Badge>
                              </div>
                              <Badge variant="outline" className="text-sm px-3 py-1">
                                <Target className="h-3 w-3 mr-1" />
                                신뢰도 {modification.confidence.toFixed(1)}%
                              </Badge>
                            </div>

                            {/* 이유 설명 */}
                            <div className="bg-blue-50 p-3 rounded-lg border-l-4 border-blue-400">
                              <div className="text-sm font-semibold text-blue-900 mb-1">
                                💡 수정 이유
                              </div>
                              <div className="text-sm text-blue-800">
                                {modification.reason}
                              </div>
                            </div>

                            {/* 텍스트 비교 */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                              {/* 원본 */}
                              <div className="space-y-2">
                                <div className="flex items-center gap-2 text-sm font-bold text-red-700">
                                  <div className="w-2 h-2 rounded-full bg-red-500"></div>
                                  변경 전
                                </div>
                                <div className="bg-red-50 border-2 border-red-200 rounded-lg p-4 min-h-[80px]">
                                  <div className="text-base leading-relaxed text-gray-800">
                                    "{modification.original_text}"
                                  </div>
                                </div>
                              </div>

                              {/* 수정본 */}
                              <div className="space-y-2">
                                <div className="flex items-center gap-2 text-sm font-bold text-green-700">
                                  <div className="w-2 h-2 rounded-full bg-green-500"></div>
                                  변경 후
                                </div>
                                <div className="bg-green-50 border-2 border-green-200 rounded-lg p-4 min-h-[80px]">
                                  <div className="text-base leading-relaxed text-gray-800">
                                    "{modification.modified_text}"
                                  </div>
                                </div>
                              </div>
                            </div>

                            {/* 위치 정보 */}
                            <div className="flex items-center gap-3 text-xs text-gray-500 pt-2">
                              <span>📍 위치: {modification.start_index} ~ {modification.end_index}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </ScrollArea>
                  </CardContent>
                </CollapsibleContent>
              </Collapsible>
            </Card>
          )}

              {/* 성공 메시지 */}
              {avoidanceResult.success && (
                <Card className="border-green-200 bg-green-50">
                  <CardContent className="pt-6">
                    <div className="flex items-center gap-2 text-green-700">
                      <CheckCircle className="h-5 w-5" />
                      <span className="font-medium">{avoidanceResult.message}</span>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* 모달 하단 버튼 */}
              <div className="flex justify-end gap-3 pt-4 border-t">
                <Button
                  variant="outline"
                  onClick={() => copyToClipboard(avoidanceResult.rewritten_text)}
                >
                  <Copy className="h-4 w-4 mr-2" />
                  재작성 텍스트 복사
                </Button>
                <Button
                  variant="outline"
                  onClick={handleDownloadResult}
                >
                  <Download className="h-4 w-4 mr-2" />
                  결과 다운로드
                </Button>
                <Button onClick={() => setShowResultModal(false)}>
                  닫기
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default AIPlagiarismAvoidance;