import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Shield, Zap, Target, Brain, TrendingDown, BarChart3 } from "lucide-react";
import { useNavigate } from "react-router-dom";
import AIPlagiarismAvoidance from "@/components/AIPlagiarismAvoidance";

const AIPlagiarismAvoidancePage = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 헤더 */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate("/")}
                className="flex items-center gap-2"
              >
                <ArrowLeft className="h-4 w-4" />
                홈으로 돌아가기
              </Button>
            </div>
            <div className="text-right">
              <h1 className="text-xl font-bold text-gray-900">AI 표절 회피 시스템</h1>
              <p className="text-sm text-gray-500">CopyKiller AI</p>
            </div>
          </div>
        </div>
      </div>

      {/* 메인 컨텐츠 */}
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* 소개 섹션 */}
          <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-0">
            <CardHeader className="text-center">
              <CardTitle className="flex items-center justify-center gap-3 text-2xl">
                <Shield className="h-8 w-8 text-blue-600" />
                AI 표절 회피 시스템
              </CardTitle>
              <CardDescription className="text-lg mt-2">
                인공지능이 표절 위험 텍스트를 자동으로 감지하고 재작성하여 유사도를 낮춥니다
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="text-center p-4">
                  <div className="inline-flex items-center justify-center w-12 h-12 bg-blue-100 rounded-lg mb-3">
                    <Target className="h-6 w-6 text-blue-600" />
                  </div>
                  <h3 className="font-semibold text-gray-900">정확한 탐지</h3>
                  <p className="text-sm text-gray-600 mt-1">
                    표절 위험 부분을 정확히 식별
                  </p>
                </div>
                <div className="text-center p-4">
                  <div className="inline-flex items-center justify-center w-12 h-12 bg-green-100 rounded-lg mb-3">
                    <Brain className="h-6 w-6 text-green-600" />
                  </div>
                  <h3 className="font-semibold text-gray-900">지능형 재작성</h3>
                  <p className="text-sm text-gray-600 mt-1">
                    의미를 보존하며 자연스럽게 변환
                  </p>
                </div>
                <div className="text-center p-4">
                  <div className="inline-flex items-center justify-center w-12 h-12 bg-purple-100 rounded-lg mb-3">
                    <TrendingDown className="h-6 w-6 text-purple-600" />
                  </div>
                  <h3 className="font-semibold text-gray-900">유사도 감소</h3>
                  <p className="text-sm text-gray-600 mt-1">
                    효과적으로 표절 점수 낮춤
                  </p>
                </div>
                <div className="text-center p-4">
                  <div className="inline-flex items-center justify-center w-12 h-12 bg-orange-100 rounded-lg mb-3">
                    <BarChart3 className="h-6 w-6 text-orange-600" />
                  </div>
                  <h3 className="font-semibold text-gray-900">상세 분석</h3>
                  <p className="text-sm text-gray-600 mt-1">
                    수정 내역과 신뢰도 제공
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 기능 설명 */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Zap className="h-5 w-5 text-yellow-500" />
                  다양한 변환 기법
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="flex items-center gap-2 text-sm">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  동의어 치환
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  문장 구조 변경
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                  표현 방식 다양화
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
                  어순 재배열
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Brain className="h-5 w-5 text-purple-500" />
                  AI 기반 처리
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="text-sm text-gray-600">
                  • 문맥을 고려한 지능적 변환
                </div>
                <div className="text-sm text-gray-600">
                  • 원본 의미 완벽 보존
                </div>
                <div className="text-sm text-gray-600">
                  • 자연스러운 한국어 표현
                </div>
                <div className="text-sm text-gray-600">
                  • 실시간 신뢰도 계산
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5 text-green-500" />
                  성능 지표
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="text-sm text-gray-600">
                  • 유사도 감소량 측정
                </div>
                <div className="text-sm text-gray-600">
                  • 수정 신뢰도 점수
                </div>
                <div className="text-sm text-gray-600">
                  • 상세한 변경 내역
                </div>
                <div className="text-sm text-gray-600">
                  • 전후 비교 분석
                </div>
              </CardContent>
            </Card>
          </div>

          {/* 사용법 안내 */}
          <Card>
            <CardHeader>
              <CardTitle>사용법 안내</CardTitle>
              <CardDescription>
                AI 표절 회피 시스템을 사용하는 두 가지 방법을 안내합니다
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-3">
                  <h4 className="font-semibold text-gray-900 flex items-center gap-2">
                    <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-bold">1</div>
                    기존 검사 결과 활용
                  </h4>
                  <div className="text-sm text-gray-600 space-y-1 pl-8">
                    <p>• 표절 검사를 먼저 실행</p>
                    <p>• 결과 화면에서 "AI 표절 회피" 버튼 클릭</p>
                    <p>• 표절 부분이 자동으로 감지 및 재작성</p>
                  </div>
                </div>
                <div className="space-y-3">
                  <h4 className="font-semibold text-gray-900 flex items-center gap-2">
                    <div className="w-6 h-6 bg-green-100 text-green-600 rounded-full flex items-center justify-center text-sm font-bold">2</div>
                    직접 텍스트 입력
                  </h4>
                  <div className="text-sm text-gray-600 space-y-1 pl-8">
                    <p>• 텍스트 직접 입력</p>
                    <p>• 유사도 임계값 설정</p>
                    <p>• 표절 검사 + 자동 회피 처리</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* AI 표절 회피 컴포넌트 */}
          <AIPlagiarismAvoidance />
        </div>
      </div>
    </div>
  );
};

export default AIPlagiarismAvoidancePage;